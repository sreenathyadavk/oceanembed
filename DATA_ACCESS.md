# OceanEmbed Data Access

## Automated API Usage
Data acquisition is mediated via programmatic toolkits, circumventing manual portal downloads to guarantee reproducible provenance.

### Copernicus Marine Service
- **Client:** `copernicusmarine` Python CLI (v2.x+).
- **Authentication:** Relies explicitly on standard environmental credentials (`COPERNICUSMARINE_SERVICE_USERNAME` and `COPERNICUSMARINE_SERVICE_PASSWORD`). Credentials are not persisted in scripts or configurations.
- **Subsetting:** Handled explicitly upstream in the `copernicusmarine subset` invocation (constraining latitude, longitude, datetime, and depths).

### INCOIS / Argo ERDDAP 
- **Endpoint:** `https://erddap.incois.gov.in/erddap/tabledap/Indian_ARGO_Floats.csv`
- **Method:** Standard HTTP Requests payloading bounding box parameters (Time, lat, lon) and strictly pulling required variables (`PRES`, `TEMP`).
- **Security Constraint:** Local Indian government SSL roots may fail standard verification natively, necessitating `verify=False` exceptions within scripts pending root cert additions.
