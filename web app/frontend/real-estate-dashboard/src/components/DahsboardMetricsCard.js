import React from 'react';
import styled from 'styled-components';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRulerCombined, faHome, faTree } from '@fortawesome/free-solid-svg-icons';

const Card = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-around;
  align-items: center;
`;

const CardTitle = styled.h3`
  font-size: 16px;
  color: #333;
  margin-bottom: 5px;
`;

const MetricContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
`;

const Icon = styled(FontAwesomeIcon)`
  color: #4a90e2;
  margin-bottom: 5px;
  font-size: 24px;
`;

// Props are now received here
const DashboardMetricsCard = ({ metrics, currency, formatCurrency, convertCurrency }) => {
  return (
    <Card>
      <MetricContainer>
        <Icon icon={faRulerCombined} />
        <CardTitle>Price per m²</CardTitle>
        <p>{formatCurrency(convertCurrency(metrics.price_per_sq_meter, currency), currency)}</p>
      </MetricContainer>
      <MetricContainer>
        <Icon icon={faHome} />
        <CardTitle>Average Interior Size</CardTitle>
        <p>{metrics.average_interior_size ? `${metrics.average_interior_size.toFixed(0)} m²` : '0 m²'}</p>
      </MetricContainer>
      <MetricContainer>
        <Icon icon={faTree} />
        <CardTitle>Average Land Size</CardTitle>
        <p>{metrics.average_land_size ? `${metrics.average_land_size.toFixed(0)} m²` : '0 m²'}</p>
      </MetricContainer>
    </Card>
  );
};

export default DashboardMetricsCard;
