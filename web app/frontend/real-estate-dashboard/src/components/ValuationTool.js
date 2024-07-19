import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const ValuationToolContainer = styled.div`
  padding: 20px;
  width: 800px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
`;

const Input = styled.input`
  padding: 10px;
  box-sizing: border-box;
`;

const Select = styled.select`
  padding: 10px;
  box-sizing: border-box;
`;

const Button = styled.button`
  padding: 10px 20px;
  background-color: #1890ff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    background-color: #40a9ff;
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
`;

const Result = styled.div`
  margin-top: 20px;
  font-size: 18px;
  font-weight: bold;
`;

const ValuationTool = () => {
  const [interiorSurface, setInteriorSurface] = useState('');
  const [landSurface, setLandSurface] = useState('');
  const [bedrooms, setBedrooms] = useState('');
  const [bathrooms, setBathrooms] = useState('');
  const [propertyType, setPropertyType] = useState('');
  const [region, setRegion] = useState('');
  const [generalFeatures, setGeneralFeatures] = useState([]);
  const [selectedGeneralFeatures, setSelectedGeneralFeatures] = useState([]);
  const [descriptionFeatures, setDescriptionFeatures] = useState([]);
  const [selectedDescriptionFeatures, setSelectedDescriptionFeatures] = useState([]);
  const [propertyTypes, setPropertyTypes] = useState([]);
  const [regions, setRegions] = useState([]);
  const [predictedPrice, setPredictedPrice] = useState(null);

  useEffect(() => {
    const fetchDistinctFeatures = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/distinct_features/');
        setGeneralFeatures(response.data.general_features || []);
        setDescriptionFeatures(response.data.description_features || []);
        setPropertyTypes(response.data.property_types || []);
        setRegions(response.data.regions || []);
      } catch (error) {
        console.error('Error fetching distinct features:', error);
      }
    };

    fetchDistinctFeatures();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      type: propertyType,
      region: region,
      interior_surface: parseFloat(interiorSurface),
      land_surface: parseFloat(landSurface),
      bedrooms: parseInt(bedrooms, 10),
      bathrooms: parseInt(bathrooms, 10),
      general_features: selectedGeneralFeatures,
      description: selectedDescriptionFeatures.join(', ')
    };

    try {
      const response = await axios.post('http://localhost:8000/api/predict/', payload, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      setPredictedPrice(response.data.predicted_price);
    } catch (error) {
      console.error('Error fetching prediction:', error);
    }
  };

  return (
    <ValuationToolContainer>
      <h1>Valuation Tool</h1>
      <form onSubmit={handleSubmit}>
        <FormGroup>
          <Label>Interior Surface (m²)</Label>
          <Input
            type="number"
            value={interiorSurface}
            onChange={(e) => setInteriorSurface(e.target.value)}
            step="0.1"
          />
        </FormGroup>
        <FormGroup>
          <Label>Land Surface (m²)</Label>
          <Input
            type="number"
            value={landSurface}
            onChange={(e) => setLandSurface(e.target.value)}
            step="0.1"
          />
        </FormGroup>
        <FormGroup>
          <Label>Bedrooms</Label>
          <Input
            type="number"
            value={bedrooms}
            onChange={(e) => setBedrooms(e.target.value)}
          />
        </FormGroup>
        <FormGroup>
          <Label>Bathrooms</Label>
          <Input
            type="number"
            value={bathrooms}
            onChange={(e) => setBathrooms(e.target.value)}
          />
        </FormGroup>
        <FormGroup>
          <Label>Property Type</Label>
          <Select value={propertyType} onChange={(e) => setPropertyType(e.target.value)}>
            <option value="">Select Property Type</option>
            {propertyTypes.map((type, index) => (
              <option key={index} value={type}>{type}</option>
            ))}
          </Select>
        </FormGroup>
        <FormGroup>
          <Label>Region</Label>
          <Select value={region} onChange={(e) => setRegion(e.target.value)}>
            <option value="">Select Region</option>
            {regions.map((reg, index) => (
              <option key={index} value={reg}>{reg}</option>
            ))}
          </Select>
        </FormGroup>
        <FormGroup>
          <Label>General Features</Label>
          <CheckboxGroup>
            {generalFeatures.map((feature, index) => (
              <CheckboxLabel key={index}>
                <input
                  type="checkbox"
                  value={feature}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedGeneralFeatures([...selectedGeneralFeatures, feature]);
                    } else {
                      setSelectedGeneralFeatures(selectedGeneralFeatures.filter(f => f !== feature));
                    }
                  }}
                />
                {feature}
              </CheckboxLabel>
            ))}
          </CheckboxGroup>
        </FormGroup>
        <FormGroup>
          <Label>Description Features</Label>
          <CheckboxGroup>
            {descriptionFeatures.map((feature, index) => (
              <CheckboxLabel key={index}>
                <input
                  type="checkbox"
                  value={feature}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedDescriptionFeatures([...selectedDescriptionFeatures, feature]);
                    } else {
                      setSelectedDescriptionFeatures(selectedDescriptionFeatures.filter(f => f !== feature));
                    }
                  }}
                />
                {feature}
              </CheckboxLabel>
            ))}
          </CheckboxGroup>
        </FormGroup>
        <Button type="submit">Get Valuation</Button>
      </form>
      {predictedPrice !== null && (
        <Result>
          Predicted Price: {predictedPrice.toLocaleString(undefined, { style: 'currency', currency: 'MUR' })}
        </Result>
      )}
    </ValuationToolContainer>
  );
};

export default ValuationTool;
