# Zeno - E-commerce Platform

Zeno is a robust e-commerce platform built with Django, featuring a complete shopping experience with secure payment integration, user authentication, and order management.

## Features

- 🛍️ **Product Management**
  - Product catalog with categories
  - Product search and filtering
  - Image handling for products

- 🔐 **User Authentication**
  - User registration and login
  - Profile management
  - Custom user model

- 🛒 **Shopping Cart**
  - Add/remove products
  - Update quantities
  - Cart persistence

- 💳 **Payment Integration**
  - Secure payment processing with Razorpay
  - Order tracking
  - Payment status management

- 📧 **Email Notifications**
  - Order confirmation emails
  - Custom email templates
  - Automated notifications

- 👤 **Admin Interface**
  - Product management
  - Order management
  - User management
  - Custom admin views

## Tech Stack

- **Backend**: Django
- **Database**: SQLite (default)
- **Payment Gateway**: Razorpay
- **Static Files**: Django static files
- **Media Handling**: Django media files
- **Templates**: Django templates

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Zeno.git
   cd Zeno
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add:
   ```
   SECRET_KEY=your_secret_key
   RAZORPAY_KEY_ID=your_razorpay_key
   RAZORPAY_KEY_SECRET=your_razorpay_secret
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
Zeno/
├── home/                   # Main application directory
│   ├── views.py           # View functions
│   ├── models.py          # Database models
│   ├── urls.py            # URL configurations
│   ├── razorpay_handler.py# Payment integration
│   └── emailer.py         # Email handling
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded files
└── Zeno/                # Project configuration
```

## Configuration

- Configure your Razorpay credentials in settings
- Set up email configuration for notifications
- Configure static and media file settings

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any queries or support, please open an issue in the GitHub repository.

---
Made with ❤️ using Django 