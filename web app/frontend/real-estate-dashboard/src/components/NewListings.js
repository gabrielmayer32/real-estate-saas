import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const LatestPropertiesContainer = styled.div`
  padding: 20px;
`;

const PropertiesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-gap: 20px;
`;

const PropertyCard = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const CardTitle = styled.h3`
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
`;

const CardLink = styled.a`
  color: #1890ff;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
`;

const Select = styled.select`
  margin-bottom: 20px;
  padding: 10px;
  font-size: 16px;
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

const NewListings = ({ currency = 'Rs', propertyType, region }) => {
  const [latestProperties, setLatestProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currencyRates, setCurrencyRates] = useState({ Rs: 1, EUR: 0.021, USD: 0.024 });
  const [sortBy, setSortBy] = useState('date_added');

  useEffect(() => {
    const fetchCurrencyRates = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/exchange_rates/');
        setCurrencyRates(response.data);
      } catch (error) {
        console.error('Error fetching exchange rates:', error);
      }
    };

    fetchCurrencyRates();
  }, []);

  const convertCurrency = (amount, currency) => {
    return amount * currencyRates[currencyCodes[currency]];
  };

  useEffect(() => {
    const fetchLatestProperties = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/latest-properties/', {
          params: {
            property_type: propertyType,
            region: region,
            sort_by: sortBy
          }
        });
        setLatestProperties(response.data.latest_properties);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLatestProperties();
  }, [propertyType, region, sortBy]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <LatestPropertiesContainer>
      <SectionTitle>New Listings</SectionTitle>
      <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="date_added">Newest First</option>
        <option value="price">Price</option>
        <option value="interior_surface">Interior Size</option>
      </Select>
      <PropertiesGrid>
        {latestProperties.length === 0 ? (
          <p>No new listings found for the selected filters.</p>
        ) : (
          latestProperties.map((property, index) => (
            <PropertyCard key={index}>
              <CardTitle>{property.title}</CardTitle>
              <p>Location: {property.location}</p>
              <p>Price: {formatCurrency(convertCurrency(property.price, currency), currency)}</p>
              <p>Interior Size: {property.interior_surface ? `${property.interior_surface} m²` : 'N/A'}</p>
              <CardLink href={property.details_link} target="_blank">View Details</CardLink>
            </PropertyCard>
          ))
        )}
      </PropertiesGrid>
    </LatestPropertiesContainer>
  );
};

export default NewListings;
