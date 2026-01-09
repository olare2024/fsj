import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, Chip } from '@mui/material';
import { 
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon
} from '@mui/icons-material';
import './StatCard.css';

const StatCard = ({
  title,
  value,
  icon,
  color = 'primary',
  trend = null,
  trendLabel = '',
  subtitle = '',
  loading = false,
  progress = null,
  unit = '',
  size = 'medium'
}) => {
  const getTrendIcon = () => {
    if (trend > 0) return <TrendingUpIcon className="trend-icon positive" />;
    if (trend < 0) return <TrendingDownIcon className="trend-icon negative" />;
    return <TrendingFlatIcon className="trend-icon neutral" />;
  };

  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
      if (val >= 1000) return `${(val / 1000).toFixed(1)}K`;
      return val.toLocaleString();
    }
    return val;
  };

  const sizeClasses = {
    small: 'stat-card-small',
    medium: 'stat-card-medium',
    large: 'stat-card-large'
  };

  return (
    <Card className={`stat-card ${sizeClasses[size]}`}>
      <CardContent>
        <Box className="stat-card-header">
          <Typography 
            variant="subtitle2" 
            className="stat-card-title"
            color="textSecondary"
          >
            {title}
          </Typography>
          {icon && (
            <Box className="stat-card-icon" style={{ color }}>
              {icon}
            </Box>
          )}
        </Box>

        {loading ? (
          <Box className="stat-card-loading">
            <LinearProgress />
          </Box>
        ) : (
          <>
            <Typography variant={size === 'small' ? 'h5' : 'h4'} className="stat-card-value">
              {formatValue(value)}
              {unit && <span className="stat-card-unit">{unit}</span>}
            </Typography>

            {subtitle && (
              <Typography variant="caption" className="stat-card-subtitle">
                {subtitle}
              </Typography>
            )}

            {(trend !== null || progress !== null) && (
              <Box className="stat-card-footer">
                {trend !== null && (
                  <Chip
                    size="small"
                    icon={getTrendIcon()}
                    label={`${trend > 0 ? '+' : ''}${trend}% ${trendLabel}`}
                    className={`trend-chip ${trend > 0 ? 'positive' : trend < 0 ? 'negative' : 'neutral'}`}
                  />
                )}

                {progress !== null && (
                  <Box className="progress-container">
                    <LinearProgress 
                      variant="determinate" 
                      value={progress} 
                      className="stat-progress"
                    />
                    <Typography variant="caption" className="progress-label">
                      {progress}%
                    </Typography>
                  </Box>
                )}
              </Box>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default StatCard;