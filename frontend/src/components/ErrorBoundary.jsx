import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import Button from './ui/Button';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });
    
    // In production, send to monitoring service (e.g., Sentry)
    if (process.env.NODE_ENV === 'production') {
      // window.analytics?.track('Error', { error: error.message, stack: error.stack });
    }
  }

  handleRefresh = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
          <Card className="max-w-lg w-full">
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 p-3 rounded-full bg-red-100 w-fit">
                <AlertTriangle className="w-12 h-12 text-red-600" />
              </div>
              <CardTitle className="text-2xl">Something went wrong</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-slate-600 text-center">
                We've encountered an unexpected error. This has been logged and we'll look into it.
              </p>
              
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mt-4 p-4 bg-slate-100 rounded-md text-sm">
                  <summary className="cursor-pointer font-medium text-slate-700 mb-2">
                    Error Details (Development Only)
                  </summary>
                  <div className="mt-2 space-y-2">
                    <div>
                      <strong className="text-red-600">Error:</strong>
                      <pre className="mt-1 text-xs overflow-auto">
                        {this.state.error.toString()}
                      </pre>
                    </div>
                    {this.state.errorInfo && (
                      <div>
                        <strong className="text-red-600">Stack:</strong>
                        <pre className="mt-1 text-xs overflow-auto">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}
              
              <div className="flex gap-3 justify-center pt-4">
                <Button
                  variant="outline"
                  onClick={this.handleGoHome}
                  icon={<Home className="w-4 h-4" />}
                >
                  Go Home
                </Button>
                <Button
                  variant="primary"
                  onClick={this.handleRefresh}
                  icon={<RefreshCw className="w-4 h-4" />}
                >
                  Refresh Page
                </Button>
              </div>
              
              <p className="text-xs text-slate-500 text-center pt-4">
                If this problem persists, please contact support with the error details above.
              </p>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
