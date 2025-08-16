import React from 'react';
import { 
  CheckCircle, 
  AlertCircle, 
  Info, 
  XCircle, 
  AlertTriangle,
  X 
} from 'lucide-react';

const statusConfig = {
  success: {
    icon: CheckCircle,
    bgColor: 'bg-accent-50',
    borderColor: 'border-accent-200',
    textColor: 'text-accent-800',
    iconColor: 'text-accent-600',
    title: 'Success'
  },
  error: {
    icon: XCircle,
    bgColor: 'bg-error-50',
    borderColor: 'border-error-200',
    textColor: 'text-error-800',
    iconColor: 'text-error-600',
    title: 'Error'
  },
  warning: {
    icon: AlertTriangle,
    bgColor: 'bg-warning-50',
    borderColor: 'border-warning-200',
    textColor: 'text-warning-800',
    iconColor: 'text-warning-600',
    title: 'Warning'
  },
  info: {
    icon: Info,
    bgColor: 'bg-primary-50',
    borderColor: 'border-primary-200',
    textColor: 'text-primary-800',
    iconColor: 'text-primary-600',
    title: 'Information'
  }
};

export const StatusMessage = ({
  type = 'info',
  title,
  message,
  onClose,
  className = '',
  showIcon = true,
  showCloseButton = false,
  persistent = false
}) => {
  const config = statusConfig[type] || statusConfig.info;
  const IconComponent = config.icon;

  return (
    <div className={`
      ${config.bgColor} 
      ${config.borderColor} 
      ${config.textColor}
      border rounded-xl p-4 shadow-sm
      ${persistent ? '' : 'animate-fade-in'}
      ${className}
    `}>
      <div className="flex items-start gap-3">
        {showIcon && (
          <IconComponent className={`h-5 w-5 ${config.iconColor} flex-shrink-0 mt-0.5`} />
        )}
        
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className="font-semibold mb-1">
              {title || config.title}
            </h4>
          )}
          {message && (
            <p className="text-sm leading-relaxed">
              {message}
            </p>
          )}
        </div>
        
        {showCloseButton && onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 p-1 rounded-lg hover:bg-white/50 transition-colors duration-200"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export const SuccessMessage = ({ title, message, ...props }) => (
  <StatusMessage type="success" title={title} message={message} {...props} />
);

export const ErrorMessage = ({ title, message, ...props }) => (
  <StatusMessage type="error" title={title} message={message} {...props} />
);

export const WarningMessage = ({ title, message, ...props }) => (
  <StatusMessage type="warning" title={title} message={message} {...props} />
);

export const InfoMessage = ({ title, message, ...props }) => (
  <StatusMessage type="info" title={title} message={message} {...props} />
);

export const ToastMessage = ({
  type = 'info',
  title,
  message,
  onClose,
  duration = 5000,
  className = ''
}) => {
  React.useEffect(() => {
    if (duration && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div className={`
      fixed top-4 right-4 z-50 max-w-sm
      animate-slide-down
      ${className}
    `}>
      <StatusMessage
        type={type}
        title={title}
        message={message}
        onClose={onClose}
        showCloseButton={true}
        className="shadow-xl"
      />
    </div>
  );
};

export const InlineStatus = ({
  type = 'info',
  message,
  className = '',
  size = 'sm'
}) => {
  const config = statusConfig[type] || statusConfig.info;
  const IconComponent = config.icon;
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2'
  };

  return (
    <div className={`
      inline-flex items-center gap-2
      ${config.bgColor} 
      ${config.borderColor} 
      ${config.textColor}
      border rounded-full ${sizeClasses[size]}
      ${className}
    `}>
      <IconComponent className={`h-3 w-3 ${config.iconColor} flex-shrink-0`} />
      <span className="font-medium">{message}</span>
    </div>
  );
};

export const StatusBanner = ({
  type = 'info',
  title,
  message,
  action,
  actionLabel,
  onAction,
  className = ''
}) => {
  const config = statusConfig[type] || statusConfig.info;
  const IconComponent = config.icon;

  return (
    <div className={`
      ${config.bgColor} 
      ${config.borderColor} 
      border-b
      ${className}
    `}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <IconComponent className={`h-5 w-5 ${config.iconColor}`} />
            <div>
              {title && (
                <h3 className={`font-semibold ${config.textColor}`}>
                  {title}
                </h3>
              )}
              {message && (
                <p className={`text-sm ${config.textColor} opacity-90`}>
                  {message}
                </p>
              )}
            </div>
          </div>
          
          {action && actionLabel && onAction && (
            <button
              onClick={onAction}
              className={`
                px-4 py-2 rounded-lg font-medium text-sm
                ${config.bgColor} 
                ${config.textColor}
                border border-current
                hover:bg-white/20 transition-colors duration-200
              `}
            >
              {actionLabel}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
