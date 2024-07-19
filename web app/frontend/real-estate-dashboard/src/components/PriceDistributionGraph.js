import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const Card = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const CardTitle = styled.h3`
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
`;

const currencyCodes = {
  'Rs': 'MUR',
  '€': 'EUR',
  '$': 'USD',
};

const formatCurrency = (amount, currency) => {
  const currencyCode = currencyCodes[currency] || currency;
  const options = {
    style: 'currency',
    currency: currencyCode,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  };

  const formatter = new Intl.NumberFormat('en-US', options);
  return formatter.format(amount);
};

const ChartContainer = styled.div`
  width: 100%;
  height: 400px;
`;

const PriceDistribution = React.memo(({ propertyType, region, location, currency }) => {
  const [priceDistribution, setPriceDistribution] = useState({ bin_edges: [], counts: [] });
  const [currencyRates, setCurrencyRates] = useState({});

  useEffect(() => {
    // Fetch exchange rates from the backend
    axios.get('http://localhost:8000/api/exchange_rates/')
      .then(response => {
        setCurrencyRates(response.data);
      })
      .catch(error => console.error('Error fetching exchange rates:', error));
  }, []);

  const convertCurrency = (amount, currency) => {
    const rate = currencyRates[currencyCodes[currency]];
    return rate ? amount * rate : NaN;
  };

  useEffect(() => {
    const params = { propertyType, region, location };
    const cacheKey = `priceDistribution-${JSON.stringify(params)}-${currency}`;

    // Attempt to load cached data
    const cachedData = sessionStorage.getItem(cacheKey);
    if (cachedData) {
      console.log("Loading data from cache");
      setPriceDistribution(JSON.parse(cachedData));
      return;
    }

    if (propertyType && region) {
      const propertyTypeParam = propertyType === 'All' ? '' : `property_type=${propertyType}&`;
      const regionParam = region === 'All' ? '' : `region=${region}&`;
      const locationParam = location ? `location=${location}&` : '';
      
      axios.get(`http://localhost:8000/api/price_distribution/?${propertyTypeParam}${regionParam}${locationParam}`)
        .then(response => {
          const newData = {
            bin_edges: response.data.bin_edges,
            counts: response.data.counts,
          };
          setPriceDistribution(newData);
          // Cache the new data
          sessionStorage.setItem(cacheKey, JSON.stringify(newData));
        })
        .catch(error => {
          console.error('Error fetching price distribution:', error);
        });
    }
  }, [propertyType, region, location, currency, currencyRates]);

  const formattedLabels = priceDistribution.bin_edges.map((edge, index) => {
    const convertedEdge = convertCurrency(edge, currency);
    return index === 0 ? `0 - ${formatCurrency(convertCurrency(5000000, currency), currency)}` : formatCurrency(convertedEdge, currency);
  });

  const data = {
    labels: formattedLabels,
    datasets: [
      {
        label: 'Number of Properties',
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
        borderWidth: 1,
        hoverBackgroundColor: 'rgba(75,192,192,0.6)',
        hoverBorderColor: 'rgba(75,192,192,1)',
        data: priceDistribution.counts,
      },
    ],
  };

  return (
    <Card>
      <CardTitle>Price Distribution</CardTitle>
      <ChartContainer>
        <Bar
          data={data}
          options={{
            maintainAspectRatio: false,
            scales: {
              x: {
                ticks: {
                  autoSkip: false,
                  maxRotation: 45,
                  minRotation: 45,
                },
              },
              y: {
                ticks: {
                  beginAtZero: true,
                },
              },
            },
            plugins: {
              legend: {
                display: true,
                position: 'top',
              },
            },
          }}
        />
      </ChartContainer>
    </Card>
  );
});

export default PriceDistribution;
