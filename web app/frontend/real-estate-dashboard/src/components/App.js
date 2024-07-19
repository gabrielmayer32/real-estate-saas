import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';

// Import your components
import Dashboard from './Dashboard';
import RealEstateAgentDashboard from './RealEstateAgentDashboard';
import ValuationTool from './ValuationTool';
import InvestmentOpportunities from './InvestmentOpportunities';
import MarketAnalysis from './MarketAnalysis';
import Navbar from './Navbar';
import MarketEvolution from './MarketEvolution';
import SoldProperties from './SoldProperties';
import NewListings from './NewListings'; // Add this line

// Styled components
const AppContainer = styled.div`
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
`;

const ContentContainer = styled.div`
  flex-grow: 1;
  overflow-y: auto;
  background-color: #f9f9f9;
`;

// Main App component
const App = () => {
  // State hooks for managing global state
  const [currency, setCurrency] = useState('Rs');
  const [propertyType, setPropertyType] = useState('All');
  const [region, setRegion] = useState('All');
  const [location, setLocation] = useState(''); // Add location state here

  return (
    <Router>
      <AppContainer>
        <Navbar
          currency={currency}
          setCurrency={setCurrency}
          propertyType={propertyType}
          setPropertyType={setPropertyType}
          region={region}
          setRegion={setRegion}
          location={location}
          setLocation={setLocation} // Pass location state to Navbar
        />
        <ContentContainer>
          <Routes>
            <Route path="/" element={<Dashboard currency={currency} setCurrency={setCurrency} propertyType={propertyType} setPropertyType={setPropertyType} region={region} setRegion={setRegion} location={location} setLocation={setLocation} />} />
            <Route path="/real-estate-agent" element={<RealEstateAgentDashboard currency={currency} setCurrency={setCurrency} propertyType={propertyType} setPropertyType={setPropertyType} region={region} setRegion={setRegion} location={location} setLocation={setLocation} />} />
            <Route path="/valuation-tool" element={<ValuationTool currency={currency} setCurrency={setCurrency} propertyType={propertyType} setPropertyType={setPropertyType} region={region} setRegion={setRegion} location={location} setLocation={setLocation} />} />
            <Route path="/market-analysis" element={<MarketEvolution currency={currency} propertyType={propertyType} region={region} location={location} />} />
            <Route path="/investment-opportunities" element={<MarketAnalysis currency={currency} propertyType={propertyType} region={region} location={location} />} />
            <Route path="/sold-properties" element={<SoldProperties currency={currency} propertyType={propertyType} region={region} location={location} />} />
            <Route path="/new-listings" element={<NewListings currency={currency} propertyType={propertyType} region={region} location={location} />} /> {/* Add this line */}
            
            {/* Add additional routes as needed */}
          </Routes>
        </ContentContainer>
      </AppContainer>
    </Router>
  );
};

export default App;
