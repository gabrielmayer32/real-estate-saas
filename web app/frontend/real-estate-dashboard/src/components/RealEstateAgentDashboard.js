import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { Table } from 'antd';
import { Pie } from 'react-chartjs-2';

const Card = styled.div`
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #f9f9f9;
  overflow-y: auto;
`;

const Content = styled.div`
  flex-grow: 1;
  padding: 40px;
  overflow-y: auto;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
`;

const CardTitle = styled.h3`
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
`;

const PieContainer = styled.div`
  width: 500px;
  height: 500px;
  margin: 0 auto;
`;

const ComparisonContainer = styled.div`
  display: flex;
  align-items: center;
  margin: 20px 0;
`;

const PriceContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 10px;
  margin-right: 20px;
  border-radius: 8px;
  background-color: ${props => (props.isAboveMarket ? '#ffcccb' : '#d4edda')};
`;

const LogoContainer = styled.div`
  flex-shrink: 0;
  margin-right: 20px;
`;

const AgencyLogo = styled.img`
  width: 100px;
  height: auto;
  border-radius: 50%;
`;

const currencyCodes = {
  'Rs': 'MUR',
  '€': 'EUR',
  '$': 'USD',
};

const formatCurrency = (amount, currency) => {
  if (isNaN(amount) || amount === null) {
    return 'N/A';
  }
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

const RealEstateAgentDashboard = ({ currency, propertyType, region, setCurrency, setPropertyType, setRegion }) => {
  const [agencyData, setAgencyData] = useState([]);
  const [currencyRates, setCurrencyRates] = useState({ Rs: 1, EUR: 0.021, USD: 0.024 });
  const [averagePricePerSqMeter, setAveragePricePerSqMeter] = useState(0);
  const [expandedKeys, setExpandedKeys] = useState([]);
  const [detailsCache, setDetailsCache] = useState({});

  const expandRow = async (record) => {
    const queryParams = new URLSearchParams({
      agencyId: record.key,
      property_type: propertyType,
      region: region,
    }).toString();

    try {
      const response = await axios.get(`http://localhost:8000/api/agency-details/?${queryParams}`);
      const details = response.data;
      setDetailsCache((prevCache) => ({ ...prevCache, [record.key]: details }));
      return details;
    } catch (error) {
      console.error('Error fetching expanded data:', error);
      return []; // Return an empty array in case of an error
    }
  };

  const expandedRowRender = (record) => {
    const details = detailsCache[record.key];

    if (!details || details.length === 0) {
      return <p>No details available.</p>;
    }

    if (propertyType !== 'All') {
      const agencyAveragePrice = convertCurrency(details.average_price_per_sq_meter, currency);
      const marketAveragePrice = convertCurrency(averagePricePerSqMeter, currency);
      const isAboveMarket = details.average_price_per_sq_meter > averagePricePerSqMeter;

      return (
        <ComparisonContainer>
          {/* <LogoContainer>
            <AgencyLogo src={record.logo} alt={`${record.agency_name} logo`} />
          </LogoContainer> */}
          <PriceContainer isAboveMarket={isAboveMarket}>
            <p>Agency's Average Price per m²</p>
            <p>{formatCurrency(agencyAveragePrice, currency)}</p>
          </PriceContainer>
          <PriceContainer isAboveMarket={!isAboveMarket}>
            <p>Market Average Price per m²</p>
            <p>{formatCurrency(marketAveragePrice, currency)}</p>
          </PriceContainer>
        </ComparisonContainer>
      );
    } else {
      const data = {
        labels: details.property_type_distribution.map(item => item.type),
        datasets: [{
          data: details.property_type_distribution.map(item => item.count),
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#F7464A', '#949FB1', '#AC64AD'],
          hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#F7464A', '#949FB1', '#AC64AD']
        }]
      };

      return (
        <PieContainer>
          <Pie data={data} />
        </PieContainer>
      );
    }
  };

  useEffect(() => {
    axios.get('http://localhost:8000/api/exchange_rates/')
      .then(response => {
        setCurrencyRates(response.data);
      })
      .catch(error => console.error('Error fetching exchange rates:', error));
  }, []);

  const convertCurrency = (amount, currency) => {
    if (currency === 'MUR') return amount; // If the currency is MUR, no conversion needed
    return amount * currencyRates[currencyCodes[currency]];
  };

  useEffect(() => {
    const propertyTypeParam = propertyType && propertyType !== 'All' ? `property_type=${propertyType}&` : '';
    const regionParam = region && region !== 'All' ? `region=${region}&` : '';
    const url = `http://localhost:8000/api/agency-ranking/?${propertyTypeParam}${regionParam}`;

    axios.get(url)
      .then(response => {
        const formattedData = response.data.map(agency => ({
          ...agency,
          key: agency.agency_id  // ensure this key is unique and correctly identified
        }));
        console.log("Formatted Data:", formattedData);
        setAgencyData(formattedData);
        setDetailsCache({});  // Clear the details cache
        setExpandedKeys([]);  // Clear the expanded keys
      })
      .catch(error => console.error('Error fetching agency data:', error));
  }, [propertyType, region]);

  useEffect(() => {
    if (propertyType !== 'All') {
      const propertyTypeParam = propertyType ? `property_type=${propertyType}&` : '';
      const regionParam = region ? `region=${region}&` : '';
      const url = `http://localhost:8000/api/average-price-per-sq-meter/?${propertyTypeParam}${regionParam}`;

      axios.get(url)
        .then(response => {
          setAveragePricePerSqMeter(response.data.average_price_per_sq_meter);
        })
        .catch(error => console.error('Error fetching average price per sq meter:', error));
    }
  }, [propertyType, region]);

  const columns = [
    {
      title: 'Agency',
      dataIndex: 'agency_name',  // Use the correct key name
      key: 'agency_name',
    },
    {
      title: 'Number of Properties',
      dataIndex: 'property_count',
      key: 'property_count',
    },
    {
      title: 'Total Value',
      dataIndex: 'total_value',
      key: 'total_value',
      render: value => formatCurrency(convertCurrency(value, currency), currency),
    },
  ];

  return (
    <DashboardContainer>
      <Content>
        <SectionTitle>Agency Ranking</SectionTitle>
        <Card>
          <Table
            columns={columns}
            dataSource={agencyData}
            rowKey="agency_id"
            pagination={false}
            expandable={{
              expandedRowRender: record => {
                console.log("expandedRowRender called for:", record);
                return expandedRowRender(record);
              },
              onExpand: (expanded, record) => {
                console.log("Expand called:", expanded, "for record:", record);
                if (expanded) {
                  expandRow(record).then(details => {
                    const updatedData = agencyData.map(item => 
                      item.key === record.key ? { ...item, details } : item
                    );
                    setAgencyData(updatedData);
                    setExpandedKeys(prevKeys => [...prevKeys, record.key]);
                  });
                } else {
                  setExpandedKeys(prevKeys => prevKeys.filter(key => key !== record.key));
                }
              },
              expandedRowKeys: expandedKeys,
            }}
          />
        </Card>
      </Content>
    </DashboardContainer>
  );
};

export default RealEstateAgentDashboard;
