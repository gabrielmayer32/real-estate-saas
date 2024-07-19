// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './components/App';
import 'antd/dist/reset.css'; // Import Ant Design reset styles


ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
