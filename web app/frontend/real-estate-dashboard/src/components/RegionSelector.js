import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import Select from 'react-select';

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

const regions = ['All', 'West', 'East', 'North', 'South', 'Center'];

const RegionSelector = ({ region, setRegion, locations, setLocations }) => {
  const [locationOptions, setLocationOptions] = useState([]);

  useEffect(() => {
    if (region && region !== 'All') {
      axios.get(`http://localhost:8000/api/locations/?region=${region}`)
        .then(response => {
          const options = response.data.map(loc => ({
            value: loc.id,
            label: loc.name
          }));
          setLocationOptions(options);
        })
        .catch(error => {
          console.error('Error fetching locations:', error);
        });
    } else {
      setLocationOptions([]);
      setLocations([]);
    }
  }, [region, locations]);

  const handleLocationChange = (selectedOptions) => {
    setLocations(selectedOptions || []);
    console.log('Locations selected:', selectedOptions); // Add debug log
  };

  return (
    <SelectorContainer>
      {regions.map(reg => (
        <Button
          key={reg}
          active={region === reg}
          onClick={() => {
            setRegion(reg);
            setLocations([]);
            console.log('Region selected:', reg); // Add debug log
          }}
        >
          {reg}
        </Button>
      ))}
      {region && region !== 'All' && (
        <Select
          isMulti
          options={locationOptions}
          value={locations}
          onChange={handleLocationChange}
          placeholder="Select Locations"
          styles={{
            container: provided => ({ ...provided, marginTop: 5, width: '200px' }),
            menu: provided => ({ ...provided, fontSize: '12px' }),
            control: provided => ({ ...provided, fontSize: '12px' })
          }}
        />
      )}
    </SelectorContainer>
  );
};

export default RegionSelector;
