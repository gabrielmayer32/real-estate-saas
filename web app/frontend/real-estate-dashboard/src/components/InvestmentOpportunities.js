import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const InvestmentOpportunitiesContainer = styled.div`
  padding: 20px;
`;

const OpportunitiesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); // Adjusts the number of columns based on the available width
  grid-gap: 20px; // Space between the cards
`;

const OpportunityCard = styled.div`
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

const InvestmentOpportunities = ({ propertyType, region }) => {
  const [overvalued, setOvervalued] = useState([]);
  const [undervalued, setUndervalued] = useState([]);

  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/investment-opportunities/', {
          params: { property_type: propertyType, region: region }
        });
        setOvervalued(response.data.overvalued);
        setUndervalued(response.data.undervalued);
      } catch (error) {
        console.error('Error fetching investment opportunities:', error);
      }
    };

    fetchOpportunities();
  }, [propertyType, region]);

  return (
    <InvestmentOpportunitiesContainer>
      <SectionTitle>Overvalued Properties</SectionTitle>
      <OpportunitiesGrid>
        {overvalued.length === 0 ? (
          <p>No overvalued properties found for the selected filters.</p>
        ) : (
          overvalued.map((opportunity, index) => (
            <OpportunityCard key={index}>
              <CardTitle>{opportunity.title}</CardTitle>
              <p>Location: {opportunity.location}</p>
              <p>Price: {opportunity.price.toLocaleString(undefined, { style: 'currency', currency: 'MUR' })}</p>
              <CardLink href={opportunity.details_link} target="_blank">View Details</CardLink>
            </OpportunityCard>
          ))
        )}
      </OpportunitiesGrid>

      <SectionTitle>Undervalued Properties</SectionTitle>
      <OpportunitiesGrid>
        {undervalued.length === 0 ? (
          <p>No undervalued properties found for the selected filters.</p>
        ) : (
          undervalued.map((opportunity, index) => (
            <OpportunityCard key={index}>
              <CardTitle>{opportunity.title}</CardTitle>
              <p>Location: {opportunity.location}</p>
              <p>Price: {opportunity.price.toLocaleString(undefined, { style: 'currency', currency: 'MUR' })}</p>
              <CardLink href={opportunity.details_link} target="_blank">View Details</CardLink>
            </OpportunityCard>
          ))
        )}
      </OpportunitiesGrid>
    </InvestmentOpportunitiesContainer>
  );
};

export default InvestmentOpportunities;
