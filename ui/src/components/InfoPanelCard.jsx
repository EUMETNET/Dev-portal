import { Card } from 'primereact/card';
import './InfoPanelCard.css';

const InfoPanelCard = ({ children }) => {
  const cardFooter = (
    <div className="info-card-footer">
      <h3 className="footer-title">Usage Instructions</h3>

      <h4 className="footer-subtitle">Get API Key</h4>
      <p className="footer-text">
        Generate your API key to access MeteoGate services. The key will appear in the panel above.
      </p>

      <h4 className="footer-subtitle">Delete API Key</h4>
      <p className="footer-text">
        Revoke your current API key if it has been compromised or is no longer needed.
      </p>

      <h4 className="footer-subtitle">Show Routes</h4>
      <p className="footer-text">
        View available API routes and your rate limits based on your group membership.
      </p>

      <h4 className="footer-subtitle footer-section-break">Using Your API Key</h4>
      <p className="footer-text">
        Include your API key in requests as a header or URL parameter.
      </p>

      <div className="code-example">
        <strong className="code-label">In header:</strong>
        <pre className="code-block">
          {`curl -H "apikey: <YOUR_API_KEY>" https://api.meteogate.eu/route`}
        </pre>
      </div>

      <div className="code-example">
        <strong className="code-label">In URL parameter:</strong>
        <pre className="code-block">
          {`curl "https://api.meteogate.eu/route?apikey=<YOUR_API_KEY>"`}
        </pre>
      </div>

      <p className="footer-docs-link">
        For complete documentation, see{' '}
        <a
          href="https://eumetnet.github.io/meteogate-documentation/"
          target="_blank"
          rel="noopener noreferrer"
        >
          MeteoGate Docs
        </a>
      </p>
    </div>
  );

  return (
    <Card footer={cardFooter}>
      <div className="infoPanel">
        {children || 'Click a button above to get started'}
      </div>
    </Card>
  );
};

export default InfoPanelCard;