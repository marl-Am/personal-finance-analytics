# 💰 Personal Finance Analytics

<div align="center">
  
  [![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://personal-finance-analytics.onrender.com)
  [![Flask](https://img.shields.io/badge/Flask-3.1.1-black?logo=flask)](https://flask.palletsprojects.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-blue?logo=postgresql)](https://supabase.com/)
  [![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0-purple?logo=bootstrap)](https://getbootstrap.com/)
  [![Chart.js](https://img.shields.io/badge/Chart.js-4.0-ff69b4?logo=chartdotjs)](https://www.chartjs.org/)
  [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
  
  <h3>Transform Your Financial Habits with Smart Analytics 📊</h3>
  
  <p>
    <strong>Personal Finance Analytics</strong> is a comprehensive web application that makes expense tracking intuitive and insightful.
    <br>Built with modern web technologies for a seamless experience across all devices.
  </p>

  [Live Demo](https://personal-finance-analytics.onrender.com) • [Features](#features) • [Tech Stack](#tech-stack) • [Installation](#installation)

</div>

---

## 📸 Screenshots

<div align="center">

### My Expenses Overview
![My Expenses Overview](assets/MyExpenses.png)
*Add/Delete expenses page with category filtering*

### Analytics & Reports
![Analytics Reports](assets/Analytics.png)
*Comprehensive reports with Chart.js and D3.js visualizations*

</div>

---

### ✨ Features

### 🔐 **Authentication & Security**
- Secure user registration with email validation
- Bcrypt password hashing with salt
- Session management with Flask-Login
- Profile management and settings

### 💳 **Expense Management**
- **CRUD Operations**: Create, read, update, and delete expenses
- **Smart Categorization**: Main categories and subcategories
- **Advanced Filtering**: By date, month, year, and category
- **Bulk Actions**: Export and import capabilities
- **Payment Methods**: Track cash, credit, debit, and digital payments

### 📊 **Analytics Dashboard**
- **6 Interactive Charts**:
  - 🍩 Category Breakdown (Doughnut)
  - 📈 12-Month Trend Analysis (Line)
  - 📊 Daily/Monthly Spending (Bar)
  - 🏆 Top 5 Categories (Horizontal Bar)
  - 💳 Payment Methods (Polar Area)
  - 🌟 Category Sunburst (D3.js)
- **Smart Insights**: AI-powered spending recommendations
- **Real-time Updates**: Charts refresh instantly with filters

### 📁 **Export Capabilities**
- **Excel Export**: Professional XLSX with formatting and summary sheets
- **PDF Reports**: Executive summaries with ReportLab
- **Data Preservation**: All exports respect current filters

### 🎨 **Modern UI/UX**
- Responsive Bootstrap 5 design
- Dark mode support (planned)
- Mobile-first approach
- Intuitive navigation with visual feedback

---

### 🛠️ Tech Stack

<table>
<tr>
<td>

### Backend
- **Framework**: Flask 3.1.1
- **ORM**: SQLAlchemy 2.0.41
- **Auth**: Flask-Login + bcrypt
- **Forms**: Flask-WTF
- **Database**: PostgreSQL (Supabase)

</td>
<td>

### Frontend
- **CSS Framework**: Bootstrap 5
- **Charts**: Chart.js 4 + D3.js 7
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JS
- **Responsive**: Mobile-first design

</td>
<td>

### DevOps
- **Hosting**: Render (Free Tier)
- **Database**: Supabase PostgreSQL
- **Version Control**: GitHub
- **CI/CD**: GitHub Integration
- **Monitoring**: Built-in logging

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (or use SQLite for development)
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/personal-finance-analytics.git
cd personal-finance-analytics
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
cp .env.example .env

# Add your configuration
SECRET_KEY=add-your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/dbname  # Or use sqlite for dev
FLASK_ENV=development
```

5. **Initialize database**
```bash
python app.py
# Database tables will be created automatically
```

6. **Run the application**
```bash
python app.py
```

Visit `http://localhost:5000` to see your app running! 🎉

---

## 📂 Project Structure

```
personal-finance-analytics/
│
├── 📁 blueprints/           # Application modules
│   ├── auth/               # Authentication (login, signup)
│   ├── user/               # User profile & settings
│   ├── expenses/           # Expense CRUD operations
│   └── analytics/          # Charts and insights
│
├── 📁 templates/            # Jinja2 HTML templates
│   ├── base.html           # Base template with navbar
│   ├── dashboard.html      # Main dashboard
│   └── [module folders]/   # Module-specific templates
│
├── 📁 static/              # Static assets
│   ├── css/               # Custom styles
│   ├── js/                # JavaScript files
│   └── img/               # Images and icons
│
├── 📄 app.py               # Application entry point
├── 📄 models.py            # SQLAlchemy models
├── 📄 extensions.py        # Flask extensions
├── 📄 categories.py        # Expense categories config
└── 📄 requirements.txt     # Python dependencies
```

---

## 🗄️ Database Schema

### Users Table
- **UUID Primary Key** for security
- **Email & Username** unique constraints
- **Password** bcrypt hashed with salt
- **Soft Delete** support
- **Optimistic Locking** with version field

### Expenses Table
- **Foreign Key** relationship to Users
- **Indexed columns** for performance
- **Decimal precision** for amounts
- **Timezone-aware** timestamps

---

## 🌍 Deployment

The application is deployed on **Render** with **Supabase PostgreSQL**:

### Key Features:
- ✅ **Persistent Storage**: Data survives service restarts
- ✅ **Auto-scaling**: Handles traffic spikes
- ✅ **SSL/TLS**: Secure connections
- ✅ **GitHub Integration**: Auto-deploy on push
- ✅ **Environment Variables**: Secure configuration

### Deploy Your Own:

1. Fork this repository
2. Create accounts on [Render](https://render.com) and [Supabase](https://supabase.com)
3. Set up PostgreSQL on Supabase
4. Create new Web Service on Render
5. Configure environment variables
6. Deploy! 🚀

---

## 📈 Performance & Optimization

- **Database Pooling**: Connection pooler for IPv4 compatibility
- **Indexed Queries**: Fast filtering and sorting
- **Lazy Loading**: Charts load on-demand
- **Responsive Images**: Optimized for different screens
- **Caching Strategy**: Browser caching for static assets

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Flask Documentation](https://flask.palletsprojects.com/) - Web framework
- [Chart.js](https://www.chartjs.org/) - Beautiful charts
- [D3.js](https://d3js.org/) - Sunburst visualization
- [Bootstrap](https://getbootstrap.com/) - UI components
- [Supabase](https://supabase.com/) - PostgreSQL hosting

---

---
