import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import PriceDistribution from './PriceDistributionGraph';
import Heatmap from './Heatmap';
import PropertyTypeDistribution from './PropertyTypeDistribution';
import ScatterPlot from './ScatterPlot';
import PriceVsAccessibleChart from './PriceVsAccessibleChart';
import DashboardMetricsCard from './DahsboardMetricsCard';

const DashboardContainer = styled.div`
  flex-grow: 1;
  height: 100%;
  width: 100%;
  background-color: #f9f9f9;
  overflow-y: auto;
`;

const Content = styled.div`
  padding: 40px;
  box-sizing: border-box;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
`;

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

const Dashboard = ({ currency, setCurrency, propertyType, setPropertyType, region, setRegion, location, setLocation }) => {
  const [currencyRates, setCurrencyRates] = useState({ Rs: 1, EUR: 0.021, USD: 0.024 });
  const [metrics, setMetrics] = useState({
    price_per_sq_meter: 0,
    average_interior_size: 0,
    average_land_size: 0,
  });
  const [currentMarketValue, setCurrentMarketValue] = useState(0);
  const [dataAvailable, setDataAvailable] = useState({ metrics: true });

  useEffect(() => {
    axios.get('http://localhost:8000/api/exchange_rates/')
      .then(response => {
        setCurrencyRates(response.data);
      })
      .catch(error => console.error('Error fetching exchange rates:', error));
  }, []);

  const convertCurrency = (amount, currency) => {
    return amount * currencyRates[currencyCodes[currency]];
  };

  useEffect(() => {
    console.log('Dependencies:', { propertyType, region, location }); // Debug log
    console.log('Dashboard useEffect triggered with location:', location); // Debug log
    if (propertyType && region) {
      const propertyTypeParam = `property_type=${propertyType}&`;
      const regionParam = region === 'All' ? '' : `region=${region}&`;
      const locationParam = location ? `location=${location}&` : '';
      console.log('Fetching metrics with params:', propertyTypeParam, regionParam, locationParam); // Debug log
      axios.get(`http://localhost:8000/api/metrics/?${propertyTypeParam}${regionParam}${locationParam}`, { timeout: 10000 })
        .then(response => {
          console.log('Metrics response:', response.data); // Debug log
          setMetrics(response.data);
          setDataAvailable(prevState => ({ ...prevState, metrics: true }));
        })
        .catch(error => {
          console.error('Error fetching metrics:', error);
          setDataAvailable(prevState => ({ ...prevState, metrics: false }));
        });
    }
  }, [propertyType, region, location]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/current_market_value/', { timeout: 10000 })
      .then(response => {
        setCurrentMarketValue(response.data.current_market_value);
      })
      .catch(error => console.error('Error fetching current market value:', error));
  }, []);

  return (
    <DashboardContainer>
      <Content>
        <SectionTitle>Sales Market Analysis and Valuation</SectionTitle>
        <Card>
          <CardTitle>Current Market Value</CardTitle>
          <p>{formatCurrency(convertCurrency(currentMarketValue, currency), currency)}</p>
        </Card>
        <Card>
          <CardTitle>Property Type Distribution</CardTitle>
          <PropertyTypeDistribution region={region} /> 
        </Card>

        <DashboardMetricsCard
          metrics={metrics}
          currency={currency}
          formatCurrency={formatCurrency}
          convertCurrency={(amount) => convertCurrency(amount, currency)}
        />

        <PriceDistribution propertyType={propertyType} region={region} currency={currency} currencyRates={currencyRates} location={location} />
        <Card>
          <CardTitle>Price vs Size</CardTitle>
          <ScatterPlot currency={currency} propertyType={propertyType} region={region} location={location} />
          </Card>
        <Card>
          <CardTitle>Price vs Foreigners Accessibility</CardTitle>
          <PriceVsAccessibleChart region={region} propertyType={propertyType} minSize={50} maxSize={500} location={location} />
        </Card>
        <SectionTitle>Listings Heat Map</SectionTitle>
        <Heatmap />
      </Content>
    </DashboardContainer>
  );
};

export default Dashboard;
