import React, { useState, useEffect } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import fetchInstance from '../../url-fetch';
import Result from '../Results/Result/Result';

import './MoreLikeThis.css';

export default function MoreLikeThis({ pageId }) {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (pageId) {
      setIsLoading(true);
      setError(null);
      
      fetchInstance('/api/morelikethis', { query: { page_id: pageId } })
        .then(response => {
          setResults(response.results || []);
          setIsLoading(false);
        })
        .catch(error => {
          console.error('Error fetching more like this:', error);
          setError('Failed to load similar articles');
          setIsLoading(false);
        });
    }
  }, [pageId]);

  if (isLoading) {
    return (
      <div className="more-like-this-loading">
        <CircularProgress />
        <p>Loading similar articles...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="more-like-this-error">
        <p>{error}</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="more-like-this-empty">
        <p>No similar articles found.</p>
      </div>
    );
  }

  const resultComponents = results.map((result, index) => (
    <Result key={index} document={result.document} />
  ));

  return (
    <div className="more-like-this-container">
      <p className="more-like-this-info">
        Showing {results.length} similar articles
      </p>
      <div className="more-like-this-results">
        {resultComponents}
      </div>
    </div>
  );
}