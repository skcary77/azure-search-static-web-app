import React, { useState, useEffect } from "react";
import { useParams } from 'react-router-dom';
import CircularProgress from '@mui/material/CircularProgress';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';

import fetchInstance from '../../url-fetch';

import "./Details.css";


function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      className="tab-panel"
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
       // Ensure it takes full width
    >
      {value === index && <Box className="tab-panel-value">{children}</Box>}
    </div>
  );
}

export default function BasicTabs() {
  const { id } = useParams();
  const [document, setDocument] = useState({});
  const [value, setValue] = React.useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    fetchInstance('/api/lookup', { query: { id } })
      .then(response => {
        console.log(JSON.stringify(response))
        const doc = response.document;
        setDocument(doc);
        setIsLoading(false);
      })
      .catch(error => {
        console.log(error);
        setIsLoading(false);
      });

  }, [id]);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  // Extract title from page_content
  const getTitle = () => {
    if (document.page_content) {
      const lines = document.page_content.split('\n');
      const titleLine = lines.find(line => line.startsWith('Title: '));
      return titleLine ? titleLine.replace('Title: ', '') : 'No Title';
    }
    return 'No Title';
  };

  // Extract content from page_content
  const getContent = () => {
    if (document.page_content) {
      const lines = document.page_content.split('\n');
      const textIndex = lines.findIndex(line => line.startsWith(' Text: '));
      return textIndex !== -1 ? lines.slice(textIndex).join('\n').replace(' Text: ', '') : '';
    }
    return '';
  };

  if (isLoading || !id || Object.keys(document).length === 0) {
    return (
      <div className="loading-container">
        <CircularProgress />
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <Box className="details-box-parent">
      <Box className="details-tab-box-header">
        <Tabs value={value} onChange={handleChange} aria-label="page-details-tabs">
          <Tab label="Article" />
          <Tab label="Raw Data" />
        </Tabs>
      </Box>
      <CustomTabPanel value={value} index={0} className="tab-panel box-content">
        <div className="card-body">
          <h5 className="card-title">{getTitle()}</h5>
          <p className="card-text">
            <strong>Journal:</strong> {document.journal || 'Unknown'}
          </p>
          <p className="card-text">
            <strong>Author:</strong> {document.author || 'Unknown Author'}
          </p>
          <p className="card-text">
            <strong>Published:</strong> {document.published_at ? new Date(document.published_at).toLocaleDateString() : 'Unknown'}
          </p>
          {document.industries && (
            <p className="card-text">
              <strong>Industries:</strong> {document.industries}
            </p>
          )}
          {document.tags && (
            <p className="card-text">
              <strong>Tags:</strong> {document.tags}
            </p>
          )}
          {document.primary_channels && (
            <p className="card-text">
              <strong>Primary Channels:</strong> {document.primary_channels}
            </p>
          )}
          {document.secondary_channels && (
            <p className="card-text">
              <strong>Secondary Channels:</strong> {document.secondary_channels}
            </p>
          )}
          {document.companies && (
            <p className="card-text">
              <strong>Companies:</strong> {document.companies}
            </p>
          )}
          {document.organizations && document.organizations.length > 0 && (
            <p className="card-text">
              <strong>Organizations:</strong> {document.organizations.join(', ')}
            </p>
          )}
          {document.people && document.people.length > 0 && (
            <p className="card-text">
              <strong>People:</strong> {document.people.join(', ')}
            </p>
          )}
          <div className="card-text">
            <strong>Content:</strong>
            <div style={{ marginTop: '10px', whiteSpace: 'pre-wrap' }}>
              {getContent()}
            </div>
          </div>
        </div>
      </CustomTabPanel>
      <CustomTabPanel value={value} index={1} className="tab-panel">
        <div className="card-body text-left card-text details-custom-tab-panel-json-div" >
          <pre><code>
            {JSON.stringify(document, null, 2)}
          </code></pre>
        </div>
      </CustomTabPanel>
    </Box>
  );
}