import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Select, Table } from 'antd';

const { Option } = Select;

const currencyCodes = {
    'Rs': 'MUR',
    '€': 'EUR',
    '$': 'USD',
};

// Ensure this function is defined outside of any other function to avoid scoping issues
const formatCurrency = (amount, currency) => {
    const currencyCode = currencyCodes[currency] || currency;
    const options = {
        style: 'currency',
        currency: currencyCode,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    };
    return new Intl.NumberFormat('en-US', options).format(amount);
};

const AgencyComparison = ({ currency }) => {
    const [selectedPersona, setSelectedPersona] = useState('house_villa');
    const [agencyData, setAgencyData] = useState([]);

    useEffect(() => {
        axios.get(`http://localhost:8000/api/properties_by_persona/?persona=${selectedPersona}`)
            .then(response => {
                setAgencyData(response.data);
            })
            .catch(error => console.error('Error fetching agency data:', error));
    }, [selectedPersona]);

    const columns = [
        { title: 'Agency', dataIndex: 'agency', key: 'agency' },
        { title: 'Number of Properties', dataIndex: 'count', key: 'count' },
        {
            title: 'Average Value',
            dataIndex: 'average_value',
            key: 'average_value',
            render: value => formatCurrency(value, currency),
        },
        {
            title: 'Max Value',
            dataIndex: 'max_value',
            key: 'max_value',
            render: value => formatCurrency(value, currency),
        },
        {
            title: 'Min Value',
            dataIndex: 'min_value',
            key: 'min_value',
            render: value => formatCurrency(value, currency),
        },
    ];

    return (
        <div>
            <Select defaultValue="house_villa" style={{ width: 120 }} onChange={setSelectedPersona}>
                <Option value="house_villa">House/Villa</Option>
                <Option value="apartment">Apartment</Option>
                <Option value="penthouse">Penthouse</Option>
            </Select>
            <Table columns={columns} dataSource={agencyData} rowKey="agency" />
        </div>
    );
};

export default AgencyComparison;
