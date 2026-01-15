# CoI - Cause of Incident
![Project Logo](static/logo2-md.png)
![GitHub License](https://img.shields.io/github/license/nathan-v/CoI)


## Overview

I didn't like how incident handling worked at some of the places I've been employed so I've been noodling on this for a while.

Sure, you can do it in Jira or other systems today but the critical components are enforcing more structure into the reporting and the visibility of the action items.

This is a work in progress.

## Features

- Incident management system
- Action item tracking
- User authentication and authorization
- Admin dashboard
- Support for multiple authentication providers

### Todos, goals, ideas

- CI/CD
- PyPi
- Test/validate Oauth providers
- Demo site
- Support 2-way action item connections to Jira and similar

## Authentication System

The application implements a flexible authentication system that supports:

1. **Local Authentication**: Traditional username/password authentication
2. **External Authentication Providers**: Integration with OAuth2 providers like Google, GitHub, etc.
3. **Flexible User Model**: Users can be authenticated through local credentials or external providers
4. **Role-based Access Control**: Admin and regular user roles

### Authentication Flow

1. **Local Authentication**:
   - Users can register and login with username/password
   - Passwords are securely hashed using Werkzeug's security utilities

2. **External Authentication**:
   - Integration with OAuth2 providers (Google, GitHub, etc.)
   - Users can authenticate through external providers
   - System handles user creation/lookup based on external provider IDs

3. **User Model**:
   - Supports both local and external authentication methods
   - Flexible attributes for different authentication providers
   - Built-in methods for checking authentication types

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CoI
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py init-db
```

5. Run the application:
```bash
python app.py
```

## CLI Commands

The application includes several CLI commands for administrative tasks:

### Create Admin User
```bash
python -m flask --app app create-admin
```
This command creates a new admin user with local authentication. It will prompt for:
- Username
- Email (optional)
- Password
- Password confirmation

The command validates that passwords match and are at least 6 characters long, and checks for existing usernames and emails.

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Configuration

The application uses a configuration system that can be extended. The current configuration includes:
- Database settings
- Secret key for sessions
- Authentication provider settings
- Local registration enabled setting

### Environment Variables for OAuth2

For external authentication to work, you need to set the following environment variables:

For Google:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET

For GitHub:
- GITHUB_CLIENT_ID
- GITHUB_CLIENT_SECRET

For Okta:
- OKTA_CLIENT_ID
- OKTA_CLIENT_SECRET
- OKTA_ORG

For AWS Cognito:
- COGNITO_CLIENT_ID
- COGNITO_CLIENT_SECRET
- COGNITO_REGION
- COGNITO_USER_POOL

### Okta Authentication

CoI is configured for optional Okta authentication. The implementation follows the same pattern as other OAuth2 providers and supports:

1. **Configuration**: Set the required environment variables (OKTA_CLIENT_ID, OKTA_CLIENT_SECRET, OKTA_ORG)
2. **Authentication Flow**: The application handles the full OAuth2 flow for Okta authentication
3. **User Management**: Users authenticated via Okta are automatically created/managed through the existing User model

The application structure is designed to work with any OAuth2 provider, making it easy to add Okta authentication without modifying core application logic.

To enable Okta authentication:
1. Set the required environment variables
2. Configure your Okta application with the appropriate redirect URI (typically `http://localhost:5000/okta/login` for development)
3. The authentication flow will automatically handle user creation and login

This approach allows for easy integration of Okta without modifying core application logic.


### AWS Cognito Authentication

CoI is configured for optional AWS Cognito authentication. The implementation follows the same pattern as other OAuth2 providers and supports:

1. **Configuration**: Set the required environment variables (COGNITO_CLIENT_ID, COGNITO_CLIENT_SECRET, COGNITO_REGION, COGNITO_USER_POOL)
2. **Authentication Flow**: The application handles the full OAuth2 flow for Cognito authentication
3. **User Management**: Users authenticated via Cognito are automatically created/managed through the existing User model

The application structure is designed to work with any OAuth2 provider, making it easy to add Cognito authentication without modifying core application logic.

To enable Cognito authentication:
1. Set the required environment variables
2. Configure your Cognito user pool with the appropriate redirect URI (typically `http://localhost:5000/cognito/login` for development)
3. The authentication flow will automatically handle user creation and login

This approach allows for easy integration of Cognito without modifying core application logic.

### Local Registration Configuration

The application supports enabling or disabling local user registration through the `LOCAL_REGISTRATION_ENABLED` environment variable. When set to `False`, users cannot register locally but can still authenticate through external providers.

Default: `True` (local registration enabled)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository.
