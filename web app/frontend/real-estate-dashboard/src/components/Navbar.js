import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Menu } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  ApartmentOutlined,
  FundOutlined,
  BarChartOutlined,
  WalletOutlined,
  FileDoneOutlined,
  FileSearchOutlined
} from '@ant-design/icons';
import CurrencyToggle from './CurrencyToggle';
import PropertyTypeSelector from './PropertyTypeSelector';
import RegionSelector from './RegionSelector';

const NavbarContainer = styled.div`
  height: 100vh;
  width: 300px;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  overflow: hidden; /* Prevents horizontal overflow */
`;

const MenuContainer = styled.div`
  flex: 1; /* Allows the menu to take remaining space */
  overflow-y: auto; /* Allows vertical scrolling if needed */
`;

const SelectorsContainer = styled.div`
  padding: 20px;
  background-color: #f5f5f5;
  overflow-y: auto; /* Makes the container scrollable */
  max-height: 70%; /* Adjust the percentage based on your layout needs */
`;

const StyledLink = styled(Link)`
  color: inherit;
  text-decoration: none;

  &:hover {
    color: inherit;
  }
`;

const Navbar = ({ currency, setCurrency, propertyType, setPropertyType, region, setRegion, location, setLocation , setLocations }) => {
  const [selectedKey, setSelectedKey] = useState('1');
  const locationHook = useLocation();

  useEffect(() => {
    switch (locationHook.pathname) {
      case '/':
        setSelectedKey('1');
        break;
      case '/real-estate-agent':
        setSelectedKey('2');
        break;
      case '/valuation-tool':
        setSelectedKey('3');
        break;
      case '/market-analysis':
        setSelectedKey('4');
        break;
      case '/investment-opportunities':
        setSelectedKey('5');
        break;
      case '/sold-properties':
        setSelectedKey('6');
        break;
      case '/new-listings':
        setSelectedKey('7');
        break;
      default:
        setSelectedKey('1');
    }
  }, [locationHook.pathname]);

  return (
    <NavbarContainer>
      <MenuContainer>
        <Menu mode="vertical" selectedKeys={[selectedKey]}>
          <Menu.Item key="1" icon={<HomeOutlined />}>
            <StyledLink to="/">Dashboard</StyledLink>
          </Menu.Item>
          <Menu.Item key="2" icon={<ApartmentOutlined />}>
            <StyledLink to="/real-estate-agent">Real Estate Agent</StyledLink>
          </Menu.Item>
          <Menu.Item key="3" icon={<FundOutlined />}>
            <StyledLink to="/valuation-tool">Valuation Tool</StyledLink>
          </Menu.Item>
          <Menu.Item key="4" icon={<BarChartOutlined />}>
            <StyledLink to="/market-analysis">Market Analysis</StyledLink>
          </Menu.Item>
          <Menu.Item key="5" icon={<WalletOutlined />}>
            <StyledLink to="/investment-opportunities">Investment Opportunities</StyledLink>
          </Menu.Item>
          <Menu.Item key="6" icon={<FileDoneOutlined />}>
            <StyledLink to="/sold-properties">Sold Properties</StyledLink>
          </Menu.Item>
          <Menu.Item key="7" icon={<FileSearchOutlined />}>
            <StyledLink to="/new-listings">New Listings</StyledLink>
          </Menu.Item>
        </Menu>
      </MenuContainer>
      {locationHook.pathname !== '/valuation-tool' && (
        <SelectorsContainer>
          <h4>Select a currency</h4>
          <CurrencyToggle currency={currency} setCurrency={setCurrency} />
          <h4>Select a property type</h4>
          <PropertyTypeSelector propertyType={propertyType} setPropertyType={setPropertyType} />
          <h4>Select a region</h4>
          <RegionSelector region={region} setRegion={setRegion} location={location} setLocation={setLocation} setLocations={setLocations} />
        </SelectorsContainer>
      )}
    </NavbarContainer>
  );
};

export default Navbar;
