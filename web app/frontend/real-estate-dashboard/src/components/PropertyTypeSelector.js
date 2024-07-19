import React from 'react';
import styled from 'styled-components';
import { HomeOutlined, ApartmentOutlined, ShopOutlined } from '@ant-design/icons';

const SelectorContainer = styled.div`
  margin-bottom: 10px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
`;

const Button = styled.button`
  background-color: ${props => (props.active ? '#1890ff' : '#eaeaea')};
  color: ${props => (props.active ? '#fff' : '#333')};
  border: none;
  padding: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  align-items: center;
  justify-content: center;
  display: inline-flex;
  &:hover {
    background-color: #40a9ff;
  }
`;

const propertyTypes = [
  { type: 'All' },
  { type: 'House / Villa', icon: <HomeOutlined /> },
  { type: 'Apartment', icon: <ApartmentOutlined /> },
  { type: 'Townhouse / Duplex', icon: <HomeOutlined /> },
  { type: 'Penthouse', icon: <HomeOutlined /> },
  { type: 'Commercial building', icon: <ShopOutlined /> },
  { type: 'Commercial space', icon: <ShopOutlined /> },
  { type: 'Hotel resort', icon: <ShopOutlined /> },
  { type: 'Office', icon: <ShopOutlined /> },
  { type: 'Residential complex/ building', icon: <ShopOutlined /> },
  { type: 'Stock-in-trade', icon: <ShopOutlined /> },
  { type: 'Warehouse', icon: <ShopOutlined /> },
  { type: 'Agricultural land', icon: <ShopOutlined /> },
  { type: 'Residential land', icon: <ShopOutlined /> },
  { type: 'Commercial land', icon: <ShopOutlined /> },
];

const PropertyTypeSelector = ({ propertyType, setPropertyType }) => (
  <SelectorContainer>
    {propertyTypes.map(({ type, icon }) => (
      <Button
        key={type}
        active={propertyType === type}
        onClick={() => setPropertyType(type)}
      >
        {icon}
        <span style={{ marginLeft: '5px' }}>{type}</span>
      </Button>
    ))}
  </SelectorContainer>
);

export default PropertyTypeSelector;
