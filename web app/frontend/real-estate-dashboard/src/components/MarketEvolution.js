import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
import styled from 'styled-components';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import { format } from 'date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const ChartContainer = styled.div`
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
`;

const MarketEvolution = ({ currency, propertyType, region, location }) => {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [{
      label: 'Average Property Prices',
      data: [],
      fill: false,
      backgroundColor: 'rgb(75, 192, 192)',
      borderColor: 'rgba(75, 192, 192, 0.2)',
    }]
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/rolling-average-prices/', {
          params: {
            property_type: propertyType,
            region: region,
            location: location
          }
        });
        console.log("API response:", response.data);  // Log the API response

        if (response.data && Array.isArray(response.data)) {
          const labels = response.data.map(data => format(new Date(data.truncated_date), 'yyyy-MM-dd'));
          const dataPoints = response.data.map(data => parseFloat(data.avg_price) || 0);

          console.log("Labels:", labels);
          console.log("Data Points:", dataPoints);

          setChartData({
            labels: labels,
            datasets: [{
              label: 'Average Property Prices',
              data: dataPoints,
              fill: false,
              backgroundColor: 'rgb(75, 192, 192)',
              borderColor: 'rgba(75, 192, 192, 0.2)',
            }]
          });
        } else {
          console.error('Unexpected data structure:', response.data);
        }
      } catch (error) {
        console.error('Failed to fetch rolling average prices:', error);
      }
    };

    fetchData();
  }, [propertyType, region, location]);

  return (
    <ChartContainer>
      <h2>Market Evolution</h2>
      <Line
        data={chartData}
        options={{
          scales: {
            x: {
              type: 'time',
              time: {
                unit: 'day',
                tooltipFormat: 'yyyy-MM-dd'
              }
            },
            y: {
              beginAtZero: true
            }
          },
          responsive: true,
          plugins: {
            legend: {
              position: 'top',
            }
          }
        }}
      />
    </ChartContainer>
  );
};

export default MarketEvolution;
