import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const SelectorContainer = styled.div`
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
  margin-top: 5px;
  width: 80px;
  margin-right: 20px;

  &:hover {
    background-color: #40a9ff;
  }
`;

const Dropdown = styled.select`
  padding: 10px;
  margin-top: 5px;
  font-size: 12px;
  width: 200px;
`;

const regions = ['All', 'West', 'East', 'North', 'South', 'Center'];

const RegionSelector = ({ region, setRegion, location, setLocation }) => {
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    if (region && region !== 'All') {
      axios.get(`http://localhost:8000/api/locations/?region=${region}`)
        .then(response => {
          setLocations(response.data);
        })
        .catch(error => {
          console.error('Error fetching locations:', error);
        });
    } else {
      setLocations([]);
      setLocation('');
    }
  }, [region]);

  const handleLocationChange = (e) => {
    setLocation(e.target.value);
    console.log('Location selected:', e.target.value); // Add debug log
  };

  return (
    <SelectorContainer>
      {regions.map(reg => (
        <Button
          key={reg}
          active={region === reg}
          onClick={() => {
            setRegion(reg);
            setLocation('');
            console.log('Region selected:', reg); // Add debug log
          }}
        >
          {reg}
        </Button>
      ))}
      {region && region !== 'All' && (
        <Dropdown
          value={location}
          onChange={handleLocationChange}
        >
          <option value="">Select Location</option>
          {locations.map(loc => (
            <option key={loc.id} value={loc.name}>
              {loc.name}
            </option>
          ))}
        </Dropdown>
      )}
    </SelectorContainer>
  );
};

export default RegionSelector;
