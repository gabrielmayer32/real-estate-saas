// src/components/CurrencyToggle.js
import React from 'react';
import styled from 'styled-components';

const ToggleContainer = styled.div`
  margin-bottom: 20px;
`;

const Button = styled.button`
  background-color: ${props => (props.active ? '#1890ff' : '#eaeaea')};
  color: ${props => (props.active ? '#fff' : '#333')};
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 10px;
  width: 40px;
  align-items: center;
  justify-content: center;
  display: inline-flex;

  &:hover {
    background-color: #40a9ff;
  }
`;

const currencies = ['Rs', '€', '$'];

const CurrencyToggle = ({ currency, setCurrency }) => (
  <ToggleContainer>
    {currencies.map(curr => (
      <Button
        key={curr}
        active={currency === curr}
        onClick={() => setCurrency(curr)}
      >
        {curr}
      </Button>
    ))}
  </ToggleContainer>
);

export default CurrencyToggle;
