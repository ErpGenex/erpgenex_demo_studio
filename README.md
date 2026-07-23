# ERPGenex Demo Studio

## Enterprise Demo Lifecycle Management Platform

### Overview

ERPGenex Demo Studio is the official enterprise platform responsible for demo lifecycle management across all ERPGenex applications. It provides a comprehensive solution for:

- Demo Environment Management
- Demo Company Generation
- Demo Branch Generation
- Demo Data Generation
- Demo Dataset Management
- Demo Reset and Cleanup
- Demo Versioning
- Demo Templates
- Demo Marketplace
- Demo Validation and Audit

### Key Features

- **Enterprise-Grade Data Generation**: Generates realistic business environments that simulate real companies operating for several years
- **Provider System**: Extensible architecture allowing applications to register their own demo data providers
- **Safety Mechanisms**: All demo records are marked with demo IDs for safe deletion without affecting production data
- **Background Processing**: Efficient generation using background jobs with progress monitoring
- **Validation System**: Comprehensive validation of generated demo environments
- **Audit Trail**: Complete audit logging for all demo operations

### Architecture

The application follows Frappe best practices and is completely independent:

- **Core DocTypes**: Demo Environment, Demo Template, Demo Provider, Demo Generation Job
- **Generation Engine**: Modular generation system with pluggable data generators
- **Provider Registry**: Automatic discovery and registration of demo providers from installed apps
- **Safety Layer**: Protection mechanisms to ensure demo data never interferes with production data
- **API Layer**: RESTful API for all demo operations

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app erpgenex_demo_studio
```

### Requirements

- **omnexa_core**: Required dependency for core platform services
- **Frappe Framework**: Compatible with Frappe v15+

### Usage

After installation, the "Demo Studio" workspace will be available in your Frappe Desk. From there you can:

1. **Create Demo Templates**: Define templates for different industries and business scenarios
2. **Generate Demo Environments**: Create complete demo environments based on templates
3. **Monitor Generation Jobs**: Track progress of demo generation in real-time
4. **Manage Demo Providers**: View and manage registered demo data providers
5. **Validate Environments**: Run validation checks on demo environments

### API Endpoints

The application provides several whitelisted API endpoints:

- `erpgenex_demo_studio.api.demo_api.get_demo_statistics()` - Get overall demo statistics
- `erpgenex_demo_studio.api.demo_api.get_demo_environments()` - Get demo environments with filters
- `erpgenex_demo_studio.api.demo_api.validate_demo_environment()` - Validate a demo environment
- `erpgenex_demo_studio.api.demo_api.export_demo_environment()` - Export demo configuration
- `erpgenex_demo_studio.api.demo_api.import_demo_environment()` - Import demo configuration
- `erpgenex_demo_studio.api.demo_api.health_check()` - Perform health check on demo studio

### Extensibility

Applications can extend the Demo Studio by registering their own demo providers:

1. Create a Demo Provider record in the system
2. Specify the provider type (Industry Provider, Data Provider, Scenario Provider, etc.)
3. Configure the implementation details (app name, module, class, method)
4. Define supported industries and DocTypes
5. The provider will be automatically discovered and used during demo generation

### Safety and Security

- **Demo Marking**: All generated records are marked with demo IDs
- **Safe Deletion**: Only demo records can be deleted through the demo studio
- **Role-Based Access**: Demo Studio Manager role for demo operations
- **Audit Logging**: Complete audit trail for all demo operations
- **Background Processing**: Long-running operations use background jobs

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/erpgenex_demo_studio
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

### License

mit
