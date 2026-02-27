import './Header.css';

const Header = () => {
  return (
    <div className="header-wrapper">
      <div className="header-logos">
        <div className="header-logo-left">
          <img src="/eumetnet_meteogate-logo.svg" alt="MeteoGate Logo" />
        </div>
        <div className="header-logo-right">
          <img src="/co-funded_by_the_eu_white.png" alt="Co-funded by the European Union" />
        </div>
      </div>
      <div className="header-content">
        <h1>Developer Portal</h1>
        <p className="subtitle">
          <span className="highlight">Register</span> and <span className="highlight">manage</span> your API keys and{' '}
          <span className="highlight">view</span> available routes
        </p>
      </div>
    </div>
  );
};

export default Header;
