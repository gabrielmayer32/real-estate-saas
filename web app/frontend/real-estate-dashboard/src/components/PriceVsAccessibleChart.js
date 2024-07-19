import React, { useEffect, useState } from 'react';
import { Scatter } from 'react-chartjs-2';
import { Chart as ChartJS, ScatterController, PointElement, LinearScale, Title, Tooltip, Legend } from 'chart.js';
import axios from 'axios';
import styled from 'styled-components';

ChartJS.register(ScatterController, PointElement, LinearScale, Title, Tooltip, Legend);

const ChartContainer = styled.div`
  padding: 20px;
`;

const PriceVsAccessibleChart = React.memo(({ region, propertyType, location, minSize, maxSize }) => {
  const [chartData, setChartData] = useState({ datasets: [] });

  useEffect(() => {
    const params = { region, property_type: propertyType, location, min_size: minSize, max_size: maxSize };
    const cacheKey = `priceVsAccessible-${JSON.stringify(params)}`;

    // Attempt to load cached data
    const cachedData = sessionStorage.getItem(cacheKey);
    if (cachedData) {
      console.log("Loading data from cache");
      setChartData(JSON.parse(cachedData));
      return;
    }

    const fetchProperties = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/price_vs_accessible/', { params });
        const data = response.data;

        const accessible = data.filter(item => item.accessible_to_foreigners);
        const notAccessible = data.filter(item => !item.accessible_to_foreigners);

        const accessibleData = accessible.map(item => ({
          x: item.interior_surface,
          y: item.price,
          label: `${item.title} - ${item.location}`,
          details_link: item.details_link
        }));

        const notAccessibleData = notAccessible.map(item => ({
          x: item.interior_surface,
          y: item.price,
          label: `${item.title} - ${item.location}`,
          details_link: item.details_link
        }));

        const chartData = {
          datasets: [
            {
              label: 'Accessible to Foreigners',
              data: accessibleData,
              backgroundColor: 'rgba(75, 192, 192, 0.6)',
              borderColor: 'rgba(75, 192, 192, 1)',
              pointRadius: 5,
            },
            {
              label: 'Not Accessible to Foreigners',
              data: notAccessibleData,
              backgroundColor: 'rgba(255, 99, 132, 0.6)',
              borderColor: 'rgba(255, 99, 132, 1)',
              pointRadius: 5,
            },
          ],
        };

        // Update state with new data
        setChartData(chartData);

        // Cache data
        sessionStorage.setItem(cacheKey, JSON.stringify(chartData));
      } catch (error) {
        console.error('Error fetching property data:', error);
      }
    };

    fetchProperties();
  }, [region, propertyType, location, minSize, maxSize]);

  const handleClick = (event, elements) => {
    if (elements.length > 0) {
      const { datasetIndex, index } = elements[0];
      const url = chartData.datasets[datasetIndex].data[index].details_link;
      window.open(url, '_blank');
    }
  };

  return (
    <ChartContainer>
      <Scatter 
        data={chartData} 
        options={{
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Price vs. Accessible to Foreigners',
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `${context.raw.label}: ${context.raw.y.toLocaleString()} MUR`;
                }
              }
            },
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Interior Surface (m²)',
              },
              beginAtZero: true,
            },
            y: {
              title: {
                display: true,
                text: 'Price (MUR)',
              },
              beginAtZero: true,
            },
          },
          onClick: handleClick,
        }} 
      />
    </ChartContainer>
  );
});

export default PriceVsAccessibleChart;
