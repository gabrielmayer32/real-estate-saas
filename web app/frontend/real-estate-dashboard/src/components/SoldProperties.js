import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const SoldPropertiesContainer = styled.div`
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
  background-color: #e9ecef;
  border-left: 5px solid #6c757d;
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

const DetailLink = styled.a`
  text-decoration: none;
  color: #007bff;
  font-size: 14px;
  margin-top: 5px;
  cursor: pointer;
`;

const ExpandedDetails = styled.div`
  margin-top: 10px;
  background-color: #f1f1f1;
  padding: 10px;
  border-radius: 4px;
`;

const SoldProperties = ({ currency, propertyType, region }) => {
  const [soldProperties, setSoldProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedPropertyId, setExpandedPropertyId] = useState(null);

  useEffect(() => {
    const fetchSoldProperties = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/sold-properties/', {
          params: {
            property_type: propertyType,
            region: region
          }
        });
        setSoldProperties(response.data);
      } catch (error) {
        console.error('Error fetching sold properties:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSoldProperties();
  }, [propertyType, region]);

  const toggleExpandedDetails = (propertyId) => {
    setExpandedPropertyId(expandedPropertyId === propertyId ? null : propertyId);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <SoldPropertiesContainer>
      <SectionTitle>Sold Properties</SectionTitle>
      <PropertyList>
        {soldProperties.map(property => (
          <PropertyItem key={property.id}>
            <PropertyHeader>
              <PropertyDetails>
                <PropertyTitle>{property.title}</PropertyTitle>
                <DetailLink onClick={() => toggleExpandedDetails(property.id)}>
                  {expandedPropertyId === property.id ? 'Hide Details' : 'View Details'}
                </DetailLink>
              </PropertyDetails>
              <div>{new Date(property.date_added).toLocaleDateString()}</div>
            </PropertyHeader>
            {expandedPropertyId === property.id && (
              <ExpandedDetails>
                <p><strong>Location:</strong> {property.location}</p>
                <p><strong>Price:</strong> {property.price}</p>
                <p><strong>Description:</strong> {property.description}</p>
                <p><strong>Agency:</strong> {property.agency_name}</p>
                <p><strong>Surface Area:</strong> Land: {property.land_surface}, Interior: {property.interior_surface}</p>
                <p><strong>Swimming Pool:</strong> {property.swimming_pool}</p>
                <p><strong>Construction Year:</strong> {property.construction_year}</p>
                <p><strong>Bedrooms:</strong> {property.bedrooms}</p>
                <p><strong>Bathrooms:</strong> {property.bathrooms}</p>
                <p><strong>Toilets:</strong> {property.toilets}</p>
                <p><strong>Aircon:</strong> {property.aircon ? 'Yes' : 'No'}</p>
                <p><strong>General Features:</strong> {property.general_features}</p>
                <p><strong>Indoor Features:</strong> {property.indoor_features}</p>
                <p><strong>Outdoor Features:</strong> {property.outdoor_features}</p>
                <p><strong>Location Description:</strong> {property.location_description}</p>
                <p><strong>Type:</strong> {property.type}</p>
                <p><strong>Reference:</strong> {property.ref}</p>
              </ExpandedDetails>
            )}
          </PropertyItem>
        ))}
      </PropertyList>
    </SoldPropertiesContainer>
  );
};

export default SoldProperties;
