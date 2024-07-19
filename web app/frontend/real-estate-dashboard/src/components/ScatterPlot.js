import React, { useEffect, useState } from 'react';
import { Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, PointElement, LinearScale, Title, Tooltip, Legend } from 'chart.js';
import axios from 'axios';
import styled from 'styled-components';

ChartJS.register(PointElement, LinearScale, Title, Tooltip, Legend);

const ChartContainer = styled.div`
  padding: 20px;
`;

const ScatterPlot = React.memo(({ currency, propertyType, region, location }) => {
  const [chartData, setChartData] = useState({ datasets: [] });

  useEffect(() => {
    const params = { currency, propertyType, region, location };
    const cacheKey = `scatterPlot-${JSON.stringify(params)}`;

    // Attempt to load cached data
    const cachedData = sessionStorage.getItem(cacheKey);
    if (cachedData) {
      console.log("Loading data from cache");
      setChartData(JSON.parse(cachedData));
      return;
    }

    const fetchScatterData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/scatter_plot_data/', {
          params
        });
        const data = response.data;
        const points = data.map(item => ({
          x: item.interior_surface || item.land_surface, // Use either interior_surface or land_surface based on availability
          y: item.price,
        }));

        const newChartData = {
          datasets: [
            {
              label: 'Price vs. Size',
              data: points,
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1,
              pointRadius: 5,
            },
          ],
        };

        setChartData(newChartData);
        // Cache data
        sessionStorage.setItem(cacheKey, JSON.stringify(newChartData));
      } catch (error) {
        console.error('Error fetching scatter plot data:', error);
      }
    };

    fetchScatterData();
  }, [currency, propertyType, region, location]);

  return (
    <ChartContainer>
      <Scatter 
        data={chartData} 
        options={{
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Price vs. Size Relationships',
            },
            legend: {
              display: true,
              position: 'top',
            },
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Size (sq meters)',
              },
              beginAtZero: true,
            },
            y: {
              title: {
                display: true,
                text: `Price (${currency})`,
              },
              beginAtZero: true,
            },
          },
        }} 
      />
    </ChartContainer>
  );
});

export default ScatterPlot;
