import React, { useEffect, useState } from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from 'chart.js';
import axios from 'axios';
import styled from 'styled-components';

ChartJS.register(ArcElement, Tooltip, Legend, Title);

const ChartContainer = styled.div`
  width: 70%;
  height: 400px;
  padding: 20px;
`;



const PropertyTypeDistributionChart = React.memo(({ region }) => {
  const [chartData, setChartData] = useState({ labels: [], datasets: [] });

  useEffect(() => {
    const cacheKey = `propertyTypeDistribution-${region}`;

    // Attempt to load cached data
    const cachedData = sessionStorage.getItem(cacheKey);
    if (cachedData) {
      console.log("Loading data from cache");
      setChartData(JSON.parse(cachedData));
      return;
    }

    const fetchDistribution = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/property_type_distribution/', {
          params: { region }
        });
        const data = response.data;
        const labels = data.map(item => item.type);
        const counts = data.map(item => item.count);

        const colors = [
          'rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)', 'rgba(255, 205, 86, 0.2)', 
          'rgba(54, 162, 235, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(201, 203, 207, 0.2)', 
          'rgba(255, 159, 64, 0.2)', 'rgba(199, 199, 199, 0.2)', 'rgba(83, 102, 255, 0.2)',
          'rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 
          'rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'
        ];

        const borderColors = colors.map(color => color.replace('0.2', '1'));

        const newChartData = {
          labels,
          datasets: [
            {
              label: 'Number of Properties',
              data: counts,
              backgroundColor: colors,
              borderColor: borderColors,
              borderWidth: 1,
            },
          ],
        };

        setChartData(newChartData);
        // Cache data
        sessionStorage.setItem(cacheKey, JSON.stringify(newChartData));
      } catch (error) {
        console.error('Error fetching property type distribution:', error);
      }
    };

    fetchDistribution();
  }, [region]);

  return (
    <ChartContainer>
      <Pie 
  data={chartData} 
  options={{
    responsive: true,
    maintainAspectRatio: false,  // Important to respect the container's bounds
    plugins: {
      title: {
        display: true,
      },
      legend: {
        display: true,
        position: 'left',
      },
    },
  }}
  width={400}  // Set width
  height={400}  // Set height
/>

    </ChartContainer>
  );
});

export default PropertyTypeDistributionChart;
