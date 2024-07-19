import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import CurrencyToggle from './CurrencyToggle';
import PropertyTypeSelector from './PropertyTypeSelector';
import RegionSelector from './RegionSelector';

const MarketAnalysisContainer = styled.div`
  padding: 20px;
  background-color: #f9f9f9;
  min-height: 100vh;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
`;

const PropertyList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const PropertyItem = styled.div`
  background-color: ${props => (props.priceUp ? '#d4edda' : '#f8d7da')};
  border-left: 5px solid ${props => (props.priceUp ? '#28a745' : '#dc3545')};
  border-radius: 8px;
  padding: 10px;
`;

const PropertyHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const PropertyDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const PropertyTitle = styled.h4`
  margin: 0;
  font-size: 18px;
`;

const PriceChange = styled.div`
  font-size: 16px;
  font-weight: bold;
  color: ${props => (props.priceUp ? '#28a745' : '#dc3545')};
`;

const DetailLink = styled.a`
  text-decoration: none;
  color: #007bff;
  font-size: 14px;
  margin-top: 5px;
`;

const ViewHistoryButton = styled.button`
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 5px;
  &:hover {
    background-color: #0056b3;
  }
`;

const PriceHistory = styled.div`
  margin-top: 10px;
  padding: 10px;
  background-color: #f1f1f1;
  border-radius: 4px;
`;

const SortSelect = styled.select`
  margin-bottom: 20px;
  padding: 5px;
  font-size: 16px;
`;

const LatestPropertiesContainer = styled.div`
  margin-top: 40px;
`;

const LatestPropertyItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

const MarketAnalysis = ({ currency, propertyType, region }) => {
  const [priceChanges, setPriceChanges] = useState([]);
  const [latestProperties, setLatestProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedPropertyId, setExpandedPropertyId] = useState(null);
  const [priceHistory, setPriceHistory] = useState({});
  const [sortOrder, setSortOrder] = useState('price_change');
  const [currencyRates, setCurrencyRates] = useState({ Rs: 1, EUR: 0.021, USD: 0.024 });

  useEffect(() => {
    const fetchCurrencyRates = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/exchange_rates/');
        setCurrencyRates(response.data);
        console.log('Currency rates fetched:', response.data);
      } catch (error) {
        console.error('Error fetching exchange rates:', error);
      }
    };

    fetchCurrencyRates();
  }, []);

  const convertCurrency = (amount, currency) => {
    const rate = currencyRates[currencyCodes[currency]] || 1;
    console.log(`Converting amount: ${amount} with rate: ${rate} for currency: ${currency}`);
    return amount * rate;
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/price-changes/', {
          params: {
            start_date: '2024-06-01',
            end_date: '2024-06-30',
            property_type: propertyType,
            region: region,
            sort_by: sortOrder
          }
        });
        setPriceChanges(response.data.price_changes);
        setLatestProperties(response.data.latest_properties);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [propertyType, region, sortOrder]);

  const togglePriceHistory = async (propertyId) => {
    if (expandedPropertyId === propertyId) {
      setExpandedPropertyId(null);
      return;
    }

    if (!priceHistory[propertyId]) {
      try {
        const response = await axios.get(`http://localhost:8000/api/price-history/${propertyId}/`);
        setPriceHistory(prevState => ({
          ...prevState,
          [propertyId]: response.data
        }));
      } catch (error) {
        console.error('Error fetching price history:', error);
      }
    }

    setExpandedPropertyId(propertyId);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  // Separate properties with increasing and decreasing prices
  const increasingPrices = priceChanges.filter(change => change.price_up);
  const decreasingPrices = priceChanges.filter(change => !change.price_up);

  return (
    <MarketAnalysisContainer>
      <SectionTitle>Market Analysis: Price Changes</SectionTitle>
      <SortSelect onChange={(e) => setSortOrder(e.target.value)}>
        <option value="price_change">Sort by Price Change</option>
        <option value="interior_size">Sort by Interior Size</option>
      </SortSelect>
      <h3>Price Increases</h3>
      <PropertyList>
        {increasingPrices.map(change => (
          <PropertyItem key={change.property_id} priceUp={change.price_up}>
            <PropertyHeader>
              <PropertyDetails>
                <PropertyTitle>{change.property_title}</PropertyTitle>
                <DetailLink href={change.details_link} target="_blank" rel="noopener noreferrer">
                  View Details
                </DetailLink>
                <ViewHistoryButton onClick={() => togglePriceHistory(change.property_id)}>
                  {expandedPropertyId === change.property_id ? 'Hide Price History' : 'View Price History'}
                </ViewHistoryButton>
              </PropertyDetails>
              <PriceChange priceUp={change.price_up}>
                ↑ {formatCurrency(convertCurrency(change.previous_price, currency), currency)} → {formatCurrency(convertCurrency(change.current_price, currency), currency)} ({formatCurrency(convertCurrency(change.price_change, currency), currency)}) {change.price_change_percentage.toFixed(2)}%
              </PriceChange>
            </PropertyHeader>
            {expandedPropertyId === change.property_id && (
              <PriceHistory>
                <h5>Price History</h5>
                <ul>
                  {priceHistory[change.property_id] && priceHistory[change.property_id].map(history => (
                    <li key={history.date}>
                      {new Date(history.date).toLocaleDateString()}: {formatCurrency(convertCurrency(history.price, currency), currency)}
                    </li>
                  ))}
                </ul>
              </PriceHistory>
            )}
            <div>Price Change Date: {new Date(change.price_change_date).toLocaleDateString()}</div>
          </PropertyItem>
        ))}
      </PropertyList>
      <h3>Price Decreases</h3>
      <PropertyList>
        {decreasingPrices.map(change => (
          <PropertyItem key={change.property_id} priceUp={change.price_up}>
            <PropertyHeader>
              <PropertyDetails>
                <PropertyTitle>{change.property_title}</PropertyTitle>
                <DetailLink href={change.details_link} target="_blank" rel="noopener noreferrer">
                  View Details
                </DetailLink>
                <ViewHistoryButton onClick={() => togglePriceHistory(change.property_id)}>
                  {expandedPropertyId === change.property_id ? 'Hide Price History' : 'View Price History'}
                </ViewHistoryButton>
              </PropertyDetails>
              <PriceChange priceUp={change.price_up}>
                ↓ {formatCurrency(convertCurrency(change.previous_price, currency), currency)} → {formatCurrency(convertCurrency(change.current_price, currency), currency)} ({formatCurrency(convertCurrency(change.price_change, currency), currency)}) {change.price_change_percentage.toFixed(2)}%
              </PriceChange>
            </PropertyHeader>
            {expandedPropertyId === change.property_id && (
              <PriceHistory>
                <h5>Price History</h5>
                <ul>
                  {priceHistory[change.property_id] && priceHistory[change.property_id].map(history => (
                    <li key={history.date}>
                      {new Date(history.date).toLocaleDateString()}: {formatCurrency(convertCurrency(history.price, currency), currency)}
                    </li>
                  ))}
                </ul>
              </PriceHistory>
            )}
            <div>Price Change Date: {new Date(change.price_change_date).toLocaleDateString()}</div>
          </PropertyItem>
        ))}
      </PropertyList>
    </MarketAnalysisContainer>
  );
};

export default MarketAnalysis;
