import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './ChartCard.css';

const ChartCard = ({
  title,
  chartType = 'line',
  data,
  dataKey,
  categories = [],
  colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'],
  height = 300,
  loading = false,
  error = null,
  onRefresh,
  onDownload,
  timeRange = 'monthly',
  onTimeRangeChange,
  showControls = true,
  tooltipFormatter,
  legend = true,
  grid = true
}) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedRange, setSelectedRange] = useState(timeRange);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleRangeChange = (event) => {
    const newRange = event.target.value;
    setSelectedRange(newRange);
    onTimeRangeChange?.(newRange);
  };

  const renderChart = () => {
    if (loading) {
      return (
        <Box className="chart-loading">
          <div className="loading-spinner" />
          <Typography>Loading chart data...</Typography>
        </Box>
      );
    }

    if (error) {
      return (
        <Box className="chart-error">
          <Typography color="error">{error}</Typography>
          <IconButton onClick={onRefresh}>
            <RefreshIcon />
          </IconButton>
        </Box>
      );
    }

    if (!data || data.length === 0) {
      return (
        <Box className="chart-empty">
          <Typography>No data available</Typography>
        </Box>
      );
    }

    const commonProps = {
      data,
      margin: { top: 20, right: 30, left: 20, bottom: 20 }
    };

    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart {...commonProps}>
              {grid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey={dataKey} />
              <YAxis />
              <Tooltip formatter={tooltipFormatter} />
              {legend && <Legend />}
              {categories.map((category, index) => (
                <Line
                  key={category}
                  type="monotone"
                  dataKey={category}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <BarChart {...commonProps}>
              {grid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey={dataKey} />
              <YAxis />
              <Tooltip formatter={tooltipFormatter} />
              {legend && <Legend />}
              {categories.map((category, index) => (
                <Bar
                  key={category}
                  dataKey={category}
                  fill={colors[index % colors.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip formatter={tooltipFormatter} />
              {legend && <Legend />}
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <Card className="chart-card">
      <CardHeader
        title={title}
        action={
          showControls && (
            <Box className="chart-controls">
              {onTimeRangeChange && (
                <FormControl size="small" className="range-selector">
                  <InputLabel>Range</InputLabel>
                  <Select
                    value={selectedRange}
                    label="Range"
                    onChange={handleRangeChange}
                  >
                    <MenuItem value="daily">Daily</MenuItem>
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                    <MenuItem value="yearly">Yearly</MenuItem>
                  </Select>
                </FormControl>
              )}
              
              <IconButton
                aria-label="more"
                aria-controls="chart-menu"
                aria-haspopup="true"
                onClick={handleMenuClick}
              >
                <MoreVertIcon />
              </IconButton>
              
              <Menu
                id="chart-menu"
                anchorEl={anchorEl}
                keepMounted
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
              >
                {onRefresh && (
                  <MenuItem onClick={() => { onRefresh(); handleMenuClose(); }}>
                    <RefreshIcon fontSize="small" /> Refresh
                  </MenuItem>
                )}
                {onDownload && (
                  <MenuItem onClick={() => { onDownload(); handleMenuClose(); }}>
                    <DownloadIcon fontSize="small" /> Download Data
                  </MenuItem>
                )}
              </Menu>
            </Box>
          )
        }
      />
      <CardContent>
        {renderChart()}
      </CardContent>
    </Card>
  );
};

export default ChartCard;