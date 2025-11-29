# Admin Portal

A modern, responsive admin dashboard for managing employee data, built with **React**, **TypeScript**, and **Supabase**.

![Dashboard Preview](https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=1200&q=80)
*(Note: Replace with actual screenshot of your dashboard)*

## 🚀 Features

- **Authentication**: Secure admin login system.
- **Dashboard Overview**: Real-time statistics including Total Employees and New Joiners.
- **Employee Management**:
    - **CRUD Operations**: Create (via Excel), Read (List), Update, and Delete employees.
    - **Search & Filter**: Real-time search by name or email.
    - **Sorting**: Sortable columns for easier data navigation.
    - **Pagination**: Efficient handling of large datasets.
- **Bulk Upload**: Import employee data easily using Excel (`.xlsx`) or CSV files.
- **Responsive Design**: Fully responsive UI with a collapsible sidebar for mobile devices.

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Database & Auth**: Supabase
- **Utilities**:
    - `xlsx`: For parsing Excel files.
    - `bcryptjs`: For secure password handling.

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (v16 or higher)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)

## 📦 Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd supabase-admin-portal
    ```

2.  **Install dependencies**
    ```bash
    npm install
    ```

3.  **Environment Setup**
    Create a `.env` file in the root directory and add your Supabase credentials:
    ```env
    VITE_SUPABASE_URL=your_supabase_project_url
    VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
    ```

4.  **Database Setup**
    Ensure your Supabase database has the required tables (`users`, `admin`).
    *See [Database Schema](#-database-schema) below.*

5.  **Run the application**
    ```bash
    npm run dev
    ```

## 🗄️ Database Schema

### `users` Table
Stores employee information.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | uuid | Primary Key |
| `name` | text | Full name |
| `email` | text | Email address |
| `phone_number` | text | Contact number |
| `department` | text | Department name |
| `branch` | text | Branch location |
| `dob` | date | Date of Birth |
| `context` | text | Additional notes |
| `created_at` | timestamp | Record creation time |

### `admin` Table
Stores admin credentials.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | uuid | Primary Key |
| `email` | text | Admin email |
| `password_hash` | text | Bcrypt hashed password |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

