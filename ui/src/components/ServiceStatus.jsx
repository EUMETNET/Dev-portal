// eslint-disable-next-line no-unused-vars
import React, { useState, useEffect, useCallback } from 'react';
import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import { getServiceStatus } from '../Services/apiService';
import './ServiceStatus.css';

const severityMap = {
  up: 'success',
  degraded: 'warning',
  down: 'danger',
};

const labelMap = {
  up: 'Up',
  degraded: 'Degraded',
  down: 'Down',
};

const POLL_INTERVAL = 30;

const cardFooter = (
  <div className="status-card-footer">
    <h3 className="footer-title">About Service Status</h3>

    <p className="footer-text">
      {`Status Dashboard shows the current availability of MeteoGate services. Status is automatically refreshed every ${POLL_INTERVAL} seconds.`}
    </p>

    <h4 className="footer-subtitle">Status Indicators</h4>
    <div className="status-legend">
      <div className="status-legend-item">
        <Tag severity="success" value="Up" />
        <span>Service is operating normally</span>
      </div>
      <div className="status-legend-item">
        <Tag severity="warning" value="Degraded" />
        <span>Service is experiencing issues</span>
      </div>
      <div className="status-legend-item">
        <Tag severity="danger" value="Down" />
        <span>Service is currently unavailable</span>
      </div>
    </div>

    <p className="footer-docs-link">
      For more information, see{' '}
      <a href="https://eumetnet.github.io/meteogate-documentation/" target="_blank" rel="noopener noreferrer">
        MeteoGate Documentation
      </a>
    </p>
  </div>
);

const ServiceStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchStatus = useCallback(async () => {
    try {
      const { data, isError } = await getServiceStatus();
      if (!isError) {
        setStatus(data);
        setError(null);
      } else {
        setError('Failed to fetch service status');
        setStatus(null);
      }
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message);
      setStatus(null);
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, POLL_INTERVAL * 1000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const formatTime = (date) => {
    if (!date) return '';
    return date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <Card footer={cardFooter}>
        <p className="status-title">Loading service status...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card footer={cardFooter}>
        <h3 className="status-title">MeteoGate Service Status Dashboard</h3>
        <Tag severity="danger" value="Down" className="status-error-tag" />
        <p className="status-error-detail">The status service is temporarily unavailable. Please try again later.</p>
        {lastUpdated && <p className="status-last-updated">Last updated: {formatTime(lastUpdated)}</p>}
      </Card>
    );
  }

  return (
    <Card footer={cardFooter}>
      <h3 className="status-title">MeteoGate Service Status Dashboard</h3>
      <div className="status-overall">
        <span className="status-overall-label">Overall Status:</span>
        <div className="status-tag">
          <Tag
            severity={severityMap[status.overall] ?? 'secondary'}
            value={labelMap[status.overall] ?? status.overall}
          />
        </div>
      </div>
      <ul className="status-list">
        {status.services.length === 0 ? (
          <li className="status-list-item status-no-services">No services configured</li>
        ) : (
          status.services.map((svc) => (
            <li key={svc.name} className="status-list-item">
              <a
                href={svc.url}
                className="status-service-name status-service-link"
                target="_blank"
                rel="noopener noreferrer"
                title={svc.url}
              >
                {svc.name}
              </a>
              <div className="status-tag">
                <Tag severity={severityMap[svc.status] ?? 'secondary'} value={labelMap[svc.status] ?? svc.status} />
              </div>
            </li>
          ))
        )}
      </ul>
      {lastUpdated && <p className="status-last-updated">Last updated: {formatTime(lastUpdated)}</p>}
    </Card>
  );
};

export default ServiceStatus;
