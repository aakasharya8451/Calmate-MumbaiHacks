import os
from dotenv import load_dotenv
import psycopg2
from collections import Counter
from datetime import date
import json
import matplotlib.pyplot as plt
from openai import OpenAI
from fpdf import FPDF

# ---- Load .env ----
load_dotenv()  # This loads variables from .env into environment

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Postgres Connection (Persistent) ----
conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"),
    dbname=os.getenv("PG_DBNAME"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD")
)

conn.autocommit = True
cur = conn.cursor()

print("Connected to Postgres")

# Step 1: Get entire table data of call_reports

cur.execute("SELECT * FROM call_reports where call_duration_seconds > 0;")
rows = cur.fetchall()

print("rows:", rows)

# Step 2: Compute % positive vs negative experiences in a day, % of employees reported stress in a day, Number of Severe cases in a day

# rows already contains the call_reports table data
call_reports = rows  # store in a variable as requested

total_positive = 0
total_negative = 0

for r in call_reports:
    sentiment = r[5]   # JSONB sentiment_counts
    total_positive += sentiment.get("positive", 0)
    total_negative += sentiment.get("negative", 0)

total_sentiments = total_positive + total_negative
positive_percentage = (total_positive / total_sentiments) * 100 if total_sentiments > 0 else 0
negative_percentage = (total_negative / total_sentiments) * 100 if total_sentiments > 0 else 0


stressed_true = 0
stressed_false = 0

for r in call_reports:
    if r[4] is True:
        stressed_true += 1
    else:
        stressed_false += 1

total_calls = stressed_true + stressed_false
stressed_percentage = (stressed_true / total_calls) * 100 if total_calls > 0 else 0
non_stressed_percentage = (stressed_false / total_calls) * 100 if total_calls > 0 else 0


severe_cases = 0

for r in call_reports:
    if r[8] is True:
        severe_cases += 1

# Step 3: Compute Today's Top stressors (ranked: workload, deadlines, manager behaviour, unclear goals, politics, etc.) and Today's Tracks common blockers (Waiting for approvals Lack of clarity from manager Dependencies Resource crunch)

# column indexes in each row
STRESSORS_IDX = 6
BLOCKERS_IDX = 7

# aggregate counters
stress_counter = Counter()
blocker_counter = Counter()
rows_used = 0

for r in call_reports:
    rows_used += 1

    # top stressors field
    s_field = r[STRESSORS_IDX]
    if s_field:
        # handle if stored as list/tuple or as comma-separated string
        if isinstance(s_field, (list, tuple)):
            s_tokens = [str(x).strip() for x in s_field if str(x).strip()]
        else:
            s_tokens = [tok.strip() for tok in str(s_field).split(",") if tok.strip()]
        stress_counter.update(s_tokens)

    # common blockers field
    b_field = r[BLOCKERS_IDX]
    if b_field:
        if isinstance(b_field, (list, tuple)):
            b_tokens = [str(x).strip() for x in b_field if str(x).strip()]
        else:
            b_tokens = [tok.strip() for tok in str(b_field).split(",") if tok.strip()]
        blocker_counter.update(b_tokens)

# totals for percentage calculation
total_stress_mentions = sum(stress_counter.values())
total_blocker_mentions = sum(blocker_counter.values())

# build ranked lists (sorted by count desc, then name asc)
todaysTopstressors = []
for name, count in stress_counter.most_common():
    pct = round((count / total_stress_mentions) * 100, 1) if total_stress_mentions else 0.0
    todaysTopstressors.append({"name": name, "count": count, "pct": pct})

tracksCommonBlockers = []
for name, count in blocker_counter.most_common():
    pct = round((count / total_blocker_mentions) * 100, 1) if total_blocker_mentions else 0.0
    tracksCommonBlockers.append({"name": name, "count": count, "pct": pct})

print("Positive:", total_positive)
print("Negative:", total_negative)
print("Positive %:", positive_percentage)
print("Negative %:", negative_percentage)

print("Stressed %:", stressed_percentage)
print("Non-Stressed %:", non_stressed_percentage)

print("Severe cases:", severe_cases)

print("todaysTopstressors:")
print(json.dumps(todaysTopstressors, indent=2))
print("\ntracksCommonBlockers:")
print(json.dumps(tracksCommonBlockers, indent=2))

top_stressors_simple = [item["name"] for item in todaysTopstressors]
common_blockers_simple = [item["name"] for item in tracksCommonBlockers]

# Step 4: Enter the above computed data into daily_metrics along with date metric_date.

insert_sql = """
    INSERT INTO daily_metrics (
        metric_date,
        positive_pct,
        negative_pct,
        stress_reported_pct,
        top_stressors,
        common_blockers,
        severe_cases
    )
    VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s)
    ON CONFLICT (metric_date)
    DO UPDATE SET
        positive_pct = EXCLUDED.positive_pct,
        negative_pct = EXCLUDED.negative_pct,
        stress_reported_pct = EXCLUDED.stress_reported_pct,
        top_stressors = EXCLUDED.top_stressors,
        common_blockers = EXCLUDED.common_blockers,
        severe_cases = EXCLUDED.severe_cases;
"""

# cur.execute(
#     insert_sql,
#     (
#         date.today(),
#         positive_percentage,
#         negative_percentage,
#         stressed_percentage,
#         json.dumps(top_stressors_simple),
#         json.dumps(common_blockers_simple),
#         severe_cases
#     )
# )

# Step 5: Clear call_reports table - Don't do now, just show the code.

# cur.execute("DELETE FROM call_reports;")

# Step 6: Fetch last 5 days data from daily_metrics

cur.execute("SELECT * FROM daily_metrics ORDER BY metric_date DESC LIMIT 5;")
last_5_days = cur.fetchall()
print("Last 5 days data from daily_metrics:")
print("rows:", last_5_days)

# Step 7: Generate line graph of % positive vs negative experiences in a day, % of employees reported stress in a day, Number of Severe cases in a day based on last 5 days using matplotlib and save each graph as separate PNG files.
dates = [row[1].strftime("%d/%m/%Y") if row[1] else None for row in last_5_days]
positive_pcts = [row[2] for row in last_5_days]
negative_pcts = [row[3] for row in last_5_days]
stress_reported_pcts = [row[4] for row in last_5_days]
severe_cases_counts = [row[7] for row in last_5_days]

# Plot Positive vs Negative Experiences
plt.figure()
plt.plot(dates, positive_pcts, marker='o', label='Positive %')
plt.plot(dates, negative_pcts, marker='o', label='Negative %')
plt.xlabel('Date')
plt.ylabel('Percentage')
plt.title('Positive vs Negative Experiences Over Last 5 Days')
plt.legend()
plt.savefig('positive_vs_negative_experiences.png')

# Plot Stress Reported %
plt.figure()
plt.plot(dates, stress_reported_pcts, marker='o', label='Stress Reported %')
plt.xlabel('Date')
plt.ylabel('Percentage')
plt.title('Stress Reported % Over Last 5 Days')
plt.legend()
plt.savefig('stress_reported_percentage.png')

# Plot Severe Cases
plt.figure()
plt.plot(dates, severe_cases_counts, marker='o', label='Severe Cases')
plt.xlabel('Date')
plt.ylabel('Count')
plt.title('Severe Cases Over Last 5 Days')
plt.legend()
plt.savefig('severe_cases.png')

# Step 8: Based on the above, get some actions suggested by the OpenAI Thinking Model to be taken by the team and response in the form of JSON
prompt = f"""
You are to output ONLY valid JSON.

Based on the following metrics over the last 5 days, suggest actions to improve employee well-being.

Return a JSON object with:
- "shortTermSuggestions": a Python list of 2-3 short-term actions (each 1 line).
- "longTermSuggestions": a Python list of 2-3 long-term actions (each 1 line).

Metrics:
{json.dumps(last_5_days, default=str)}
"""

print("Prompt sent to OpenAI Thinking Model:")

response = client.responses.create(
    model="gpt-4o-mini",
    input=prompt
)

suggestion = response.output_text
# print(suggestion)
# print(type(suggestion))

raw_output = suggestion  # the string returned by model

# If the model wrapped JSON inside ```json ... ``` remove code fences
if raw_output.startswith("```"):
    raw_output = raw_output.strip("`")            # remove backticks
    raw_output = raw_output.split("json", 1)[-1]  # remove "json"
    raw_output = raw_output.strip()

data = json.loads(raw_output)

shortTermSuggestions = data["shortTermSuggestions"]
longTermSuggestions = data["longTermSuggestions"]

print(shortTermSuggestions) # list of 2-3 short term suggestions
print(longTermSuggestions) # list of 2-3 long term suggestions

# Step 9: Create a beautifull 1-2 page PDF report including all the above data and graphs.

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)
        self.margin = 10
        self.set_margins(self.margin, self.margin, self.margin)
        self.set_fill_color(255, 255, 255)
        
        # Colors
        self.col_primary = (52, 73, 94)    # Dark Blue/Grey
        self.col_accent = (52, 152, 219)   # Blue
        self.col_warning = (231, 76, 60)   # Red
        self.col_success = (46, 204, 113)  # Green
        self.col_text = (44, 62, 80)       # Dark Grey

    def clean_text(self, text):
        """
        Encodes to latin-1, replacing errors with '?', then decodes back.
        This prevents crashes if the AI returns emojis or special characters.
        """
        if not text:
            return ""
        return str(text).encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(*self.col_primary)
        self.cell(0, 10, 'Daily Employee Pulse Report', ln=True, align='L')
        
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f'Generated on: {date.today().strftime("%B %d, %Y")}', ln=True, align='L')
        self.ln(5)
        
        # Draw a line
        self.set_draw_color(200, 200, 200)
        self.line(self.margin, self.get_y(), 210 - self.margin, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(*self.col_primary)
        self.cell(0, 10, self.clean_text(title), ln=True)
        self.ln(2)

    def ensure_section_space(self, needed_height):
        """
        Logic: Checks if the current Y position + needed height exceeds page height.
        If so, adds a new page to keep the section together.
        """
        page_height = 297 # A4 height in mm
        bottom_margin = 15
        current_y = self.get_y()
        
        if current_y + needed_height > (page_height - bottom_margin):
            self.add_page()
            return True 
        return False

    def draw_metric_card(self, x, y, w, h, title, value, color_rgb):
        """ Draws a single metric box """
        self.set_xy(x, y)
        self.set_fill_color(*color_rgb)
        self.rect(x, y, w, h, 'F')
        
        # Title
        self.set_xy(x, y + 2)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(255, 255, 255)
        self.cell(w, 5, self.clean_text(title), align='C')
        
        # Value
        self.set_xy(x, y + 8)
        self.set_font('Helvetica', 'B', 16)
        self.cell(w, 10, self.clean_text(str(value)), align='C')

    def render_key_metrics_grid(self, pos_pct, neg_pct, stress_pct, severe):
        """ Row of 4 cards """
        h = 25
        if self.ensure_section_space(h + 15):
            pass 
            
        self.section_title("Daily Snapshot")
        
        page_width = 210 - (2 * self.margin)
        gap = 4
        card_w = (page_width - (3 * gap)) / 4
        
        y = self.get_y()
        x = self.margin
        
        # 1. Positive
        self.draw_metric_card(x, y, card_w, h, "Positive Exp", f"{round(pos_pct,1)}%", self.col_success)
        
        # 2. Negative
        x += card_w + gap
        self.draw_metric_card(x, y, card_w, h, "Negative Exp", f"{round(neg_pct,1)}%", self.col_warning)
        
        # 3. Stress
        x += card_w + gap
        self.draw_metric_card(x, y, card_w, h, "Stress Level", f"{round(stress_pct,1)}%", self.col_accent)
        
        # 4. Severe
        x += card_w + gap
        self.draw_metric_card(x, y, card_w, h, "Severe Cases", str(severe), (192, 57, 43))
        
        self.ln(h + 8)

    def render_charts_row(self, img_paths):
        """ Places images side by side horizontally """
        h_img = 40 
        
        self.ensure_section_space(h_img + 15)
        
        self.section_title("Trends (Last 5 Days)")
        
        page_width = 210 - (2 * self.margin)
        gap = 2
        img_w = (page_width - (2 * gap)) / 3
        
        y = self.get_y()
        x = self.margin
        
        for img in img_paths:
            if os.path.exists(img):
                self.image(img, x=x, y=y, w=img_w, h=h_img)
            x += img_w + gap
            
        self.ln(h_img + 8)

    def render_dual_lists(self, list1_data, list1_title, list2_data, list2_title):
        """ Renders two lists (stressors/blockers) side by side """
        
        row_h = 6
        count = max(len(list1_data), len(list2_data))
        total_h = (count * row_h) + 20 
        
        self.ensure_section_space(total_h)
        
        start_y = self.get_y()
        page_width = 210 - (2 * self.margin)
        col_w = (page_width / 2) - 5
        
        # --- Column 1 ---
        self.set_xy(self.margin, start_y)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.col_primary)
        self.cell(col_w, 8, self.clean_text(list1_title), ln=True)
        
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.col_text)
        for item in list1_data:
            # FIX: Changed '•' to '-' to avoid UnicodeEncodeError
            txt = f"- {item['name']} ({item['pct']}%)"
            self.cell(col_w, row_h, self.clean_text(txt), ln=True)
            
        # --- Column 2 ---
        max_y_col1 = self.get_y()
        self.set_xy(self.margin + col_w + 10, start_y)
        
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*self.col_primary)
        self.cell(col_w, 8, self.clean_text(list2_title), ln=True)
        
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.col_text)
        
        col2_x = self.margin + col_w + 10
        
        for item in list2_data:
            self.set_x(col2_x)
            # FIX: Changed '•' to '-' to avoid UnicodeEncodeError
            txt = f"- {item['name']} ({item['pct']}%)"
            self.cell(col_w, row_h, self.clean_text(txt), ln=True)
            
        max_y_col2 = self.get_y()
        self.set_y(max(max_y_col1, max_y_col2) + 8)

    def render_ai_suggestions(self, short_term, long_term):
        row_h = 6
        total_h = ((len(short_term) + len(long_term)) * row_h) + 30 
        
        self.ensure_section_space(total_h)
        
        self.section_title("AI Suggested Actions")
        
        # Sub-header
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.col_accent)
        
        # Short Term
        self.cell(0, 8, "Short Term (Immediate):", ln=True)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.col_text)
        for sugg in short_term:
            # Using clean_text to safely handle AI output
            self.multi_cell(0, row_h, self.clean_text(f"- {sugg}"))
        
        self.ln(2)
        
        # Long Term
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*self.col_accent)
        self.cell(0, 8, "Long Term (Strategic):", ln=True)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*self.col_text)
        for sugg in long_term:
            # Using clean_text to safely handle AI output
            self.multi_cell(0, row_h, self.clean_text(f"- {sugg}"))
            
        self.ln(5)

# ---- Execution of PDF Generation ----

pdf = PDFReport()
pdf.add_page()

# 1. Key Metrics Grid
pdf.render_key_metrics_grid(
    positive_percentage, 
    negative_percentage, 
    stressed_percentage, 
    severe_cases
)

# 2. Charts (Horizontal Wrap)
images_to_plot = [
    'positive_vs_negative_experiences.png',
    'stress_reported_percentage.png',
    'severe_cases.png'
]
pdf.render_charts_row(images_to_plot)

# 3. Tables (Side by Side)
pdf.render_dual_lists(
    todaysTopstressors[:5], "Top Stressors Today", 
    tracksCommonBlockers[:5], "Common Blockers"
)

# 4. AI Suggestions
pdf.render_ai_suggestions(shortTermSuggestions, longTermSuggestions)

# Save
pdf_filename = f"Daily_Pulse_Report_{date.today()}.pdf"
pdf.output(pdf_filename)

print(f"PDF Report generated successfully: {pdf_filename}")

# Step 10: Send this generated PDF report as an email attachment to a email addresses.
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
def send_email_with_attachment(to_address, subject, body, attachment_path):
    from_address = os.getenv("EMAIL_FROM_ADDRESS")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # Attach the body text
    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        msg.attach(part)

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

    print(f"Email sent to {to_address} with attachment {attachment_path}")

# ---- Close Postgres Connection ----
conn.commit()
cur.close()
conn.close()