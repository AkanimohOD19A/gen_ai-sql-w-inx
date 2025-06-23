# 🗃️ SQL Query Interface

A powerful Streamlit-based SQL query interface that supports multiple database types, file-to-database conversion, and AI-powered data analysis. Execute SQL queries against various databases with an intuitive web interface, complete with sample data, query history, and intelligent insights.

## 🚀 Features

### Core Functionality
- **Multi-Database Support**: SQLite, PostgreSQL, MySQL, SQL Server
- **File-to-Database Conversion**: Convert CSV/JSON files to SQLite databases
- **Sample Database**: Pre-loaded employee and department data for testing
- **Real-time Query Execution**: Execute SQL with immediate formatted results
- **Query History**: Track and reuse previous queries
- **Export Results**: Download query results as CSV files

### AI-Powered Analysis
- **Generative AI Integration**: Powered by Cohere API for intelligent data analysis
- **Automatic Data Analysis**: Get insights about your query results
- **Visualization Suggestions**: AI-recommended charts and graphs
- **Custom Analysis**: Ask specific questions about your data
- **Interactive Chat**: Conversational interface for data exploration

### Smart File Handling
- **CSV/JSON Upload**: Direct file upload with automatic conversion
- **Data Preview**: View file contents before conversion
- **Smart Sampling**: Handle large files with intelligent sampling
- **Schema Detection**: Automatic data type inference

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Database Engines**: SQLAlchemy with multiple dialect support
- **AI/ML**: Cohere API for natural language processing
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly Express (integrated with AI suggestions)
- **File Handling**: Native Python libraries with smart data type detection

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Cohere API key (for AI features)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sql-query-interface.git
   cd sql-query-interface
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

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`

## 📖 Usage Guide

### Getting Started with Sample Data

The application comes with pre-loaded sample data to help you get started immediately:

**Sample Tables:**
- `employees` - Employee records with salary and department information
- `departments` - Department data with budget information

**Sample Employee Data:**
```sql
-- View all employees
SELECT * FROM employees;

-- Find high-salary employees  
SELECT * FROM employees WHERE salary > 65000;

-- Count employees by department
SELECT department, COUNT(*) as count FROM employees GROUP BY department;

-- Join employees with department budgets
SELECT e.name, e.salary, d.budget 
FROM employees e 
JOIN departments d ON e.department = d.name;
```

### Database Connection Options

#### 1. SQLite Sample Data (Default)
- Pre-loaded with employee and department sample data
- No configuration required
- Perfect for testing and learning SQL

#### 2. File Upload & Conversion
- **CSV/JSON to SQLite**: Upload files and convert them to queryable databases
- **Direct SQLite Upload**: Upload existing `.db` files
- **Smart Features**:
  - Automatic data type detection
  - Configurable table names
  - Smart sampling for large files (default: 10,000 records)
  - Data preview before conversion

#### 3. External Databases
Configure connections to:
- **PostgreSQL** (default port: 5432)
- **MySQL** (default port: 3306) 
- **SQL Server** (with ODBC driver)

### AI-Powered Analysis

1. **Enable AI Features**
   - Toggle "Use Generative AI" in sidebar
   - Get your API key from [Cohere Dashboard](https://dashboard.cohere.com/api-keys)
   - Enter API key in the password field

2. **AI Analysis Options**
   - **Analyze Data**: Get automatic insights about your query results
   - **Suggest Visualizations**: Receive AI recommendations for charts and graphs
   - **Custom Analysis**: Ask specific questions about your data

3. **Example AI Prompts**
   ```
   "Find outliers in salary data"
   "Compare performance across departments"
   "What trends do you see in this data?"
   "Suggest ways to improve department efficiency"
   ```

## 🏗️ Project Structure

```
sql-query-interface/
├── app.py                          # Main Streamlit application
├── helper/
│   ├── gen_sql_chunk.py           # File conversion utilities
│   └── insight_gen.py             # AI analysis components
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## ⚙️ Key Components

### Database Engine Management
```python
# SQLAlchemy engines for different database types
- SQLite: sqlite:///path/to/file.db
- PostgreSQL: postgresql://user:pass@host:port/db
- MySQL: mysql+pymysql://user:pass@host:port/db
- SQL Server: mssql+pyodbc://user:pass@host:port/db
```

### File Conversion Features
- **Supported formats**: CSV, JSON
- **Auto-detection**: Data types, column names, encoding
- **Smart sampling**: Configurable record limits for large files
- **Preview mode**: See data before conversion

### AI Integration
```python
# Cohere API integration for:
- Data analysis and insights
- Visualization recommendations  
- Custom query suggestions
- Interactive data exploration
```

## 🔒 Security & Best Practices

- **SQL Injection Prevention**: All queries use SQLAlchemy's text() parameterization
- **Temporary File Management**: Secure handling of uploaded files
- **API Key Security**: Keys stored in session state, not persisted
- **Connection Validation**: Test connections before query execution

## 💡 Example Workflows

### 1. Quick Data Exploration
```sql
-- Start with sample data
SELECT * FROM employees LIMIT 5;

-- Explore structure
PRAGMA table_info(employees);

-- Basic analytics
SELECT department, AVG(salary) as avg_salary 
FROM employees 
GROUP BY department 
ORDER BY avg_salary DESC;
```

### 2. File Analysis Workflow
1. Upload CSV/JSON file
2. Preview data and configure conversion
3. Convert to SQLite database
4. Execute exploratory queries
5. Use AI analysis for insights
6. Export results

### 3. Production Database Analysis
1. Configure external database connection
2. Explore available tables
3. Execute business intelligence queries
4. Generate AI-powered insights
5. Download results for reporting

## 🛣️ Roadmap

### Planned Features
- [ ] **Enhanced Visualizations**: Direct chart generation from AI suggestions
- [ ] **Query Builder**: Visual query construction interface  
- [ ] **Scheduled Queries**: Automated query execution
- [ ] **Multi-User Support**: Session management and user authentication
- [ ] **Advanced AI Features**: Query optimization suggestions
- [ ] **Dashboard Creation**: Save and share query dashboards
- [ ] **More AI Providers**: OpenAI, Anthropic Claude integration
- [ ] **Export Formats**: Excel, PDF, JSON export options

### Current Limitations
- Large result sets may impact performance
- AI features require internet connection
- Temporary databases are session-based
- No persistent user data storage

## 🧪 Testing the Application

### Quick Test with Sample Data
1. Launch the application
2. Select "SQLite (Sample Data)" 
3. Try these sample queries:
   ```sql
   -- Basic selection
   SELECT name, salary FROM employees WHERE department = 'Engineering';
   
   -- Aggregation
   SELECT department, COUNT(*) as headcount, AVG(salary) as avg_pay 
   FROM employees GROUP BY department;
   
   -- Join operation  
   SELECT e.name, e.salary, d.budget
   FROM employees e JOIN departments d ON e.department = d.name;
   ```

### Test File Upload
1. Prepare a CSV file with sample data
2. Select "SQLite (File Upload)" 
3. Toggle "Convert my csv/json"
4. Upload file and configure conversion
5. Execute queries on converted data

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Install development dependencies
4. Make changes and test thoroughly
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings for functions
- Test with multiple database types

## 📞 Support & Resources

- **Issues**: Report bugs and request features via GitHub Issues
- **Cohere API**: [Get API key](https://dashboard.cohere.com/api-keys)
- **Streamlit Docs**: [Streamlit Documentation](https://docs.streamlit.io)
- **SQLAlchemy**: [Database engine documentation](https://docs.sqlalchemy.org)

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **Cohere** for AI-powered analysis capabilities  
- **SQLAlchemy** for robust database connectivity
- **Pandas** for data manipulation and analysis

## 📊 System Requirements

### Minimum Requirements
- **RAM**: 2GB
- **Storage**: 500MB free space
- **Python**: 3.8+

### Recommended for Large Files
- **RAM**: 4GB+  
- **Storage**: 2GB+ free space
- **CPU**: Multi-core processor

---

**Built with ❤️ using Streamlit**  
*Execute SQL queries safely and efficiently with AI-powered insights*

---

## 🔗 Quick Links

- [Cohere API Keys](https://dashboard.cohere.com/api-keys)
- [Streamlit Documentation](https://docs.streamlit.io)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)

## Promo-Images
![img.png](image_assets/img.png)
![img_1.png](image_assets/img_1.png)
![img_2.png](image_assets/img_2.png)
![img_3.png](image_assets/img_3.png)
![img_4.png](image_assets/img_4.png)
![img_5.png](image_assets/img_5.png)