# SAP Deployment Templates & Functions -  CHANGELOG
All notable changes to the SAP Deployment Manager templates will be documented in this file.

Current Templates:

- SAP ASE Linux Template (sap_ase)
- SAP ASE Windows Template (sap_ase-win)
- SAP HANA Template - Scaleup & Scaleout (sap_hana)
- SAP HANA HA Template (sap_hana_ha)
- SAP HANA Scaleout with Standby node support (sap_hana_scaleout)
- SAP MaxDB Linux Template (sap_maxdb)
- SAP MaxDB Windows Template (sap_maxdb-win)
- SAP NetWeaver Linux Template (sap_nw)
- SAP NetWeaver Windows Template (sap_nw-win)
- IBM DB2 for SAP Linux Template (sap_db2)
- IBM DB2 for SAP Windows Template (sap_db2-win)
- Two node empty SuSE pacemaker cluster (sap_emptyha)
- Two node NFS cluster using DRBD (sap_nfs)

## [4.1] 2018-11-30
### Fixed
- Fixed sapsys GID for SAP HANA in sap_hana_ha template
- Added support for SLES15
- Minor bug fixes

### Changed
- Changed SAP ASE template to use /sybase mounts instead of /ase

## [4.0] 2018-10-26
### Added
- Release sap_hana_scaleout - A SAP HANA scale-out template with support for standby nodes
- Release sap_nfs - A two node NFS cluster on SuSE using DRBD disk replication
- Released sap_emptyha - An empty two node SuSE cluster
- Release sap_db2 Linux- A Linux DB2 template for SAP applications
- Release sap_db2 Windows - A Windows DB2 template for SAP applications
- Released sap_maxdb Linux template & associated functions
- Released sap_maxdb Windows template & associated functions
- Option in all Linux templates to specify a post deployment script
- Option in all templates to specify multiple network tags


### Changed
- Bug fixes
- Switched all filesystems to use XFS as default. Some were previously EXT3


---
## [3.4] 2018-09-12
### Added
- Released sap_maxdb Linux template & associated functions
- Released sap_maxdb Windows template & associated functions


### Changed
- Bug fixes
- Removed workarounds which are no long required.

---

## [3.3] 2018-06-12
### Added
- Released sap_nw Linux template & associated functions
- Released sap_nw-win Windows template & associated functions
- Added code to ignore unexpected errors from Google API, which could cause problems with STONITH (sap_hana_ha)

---

## [3.2] 2018-06-11
### Fixed
- Fixed SLES HA cluster secondary node join when using older versions of SLES (sap_hana_ha)
- Added code to ignore unexpected errors from Google API, which could cause problems with STONITH (sap_hana_ha)

### Changed
- Improved deployment time (sap_hana_ha)
- Added a check to see if the VIP is already in use before assigning (sap_hana_ha)

----

## [3.1] 2018-06-05
### Added
- Added an option in all templates to customise the UID/GID
- Added an option in all templates to add a network tag to the instances
- Added an option in all templates to deploy without a public IP (assuming network-tag is present and configured properly - Otherwise the deployment will fail due to licensing & repositories)

### Changed
- Added some protection from those that deploy incorrectly by not calling the web version of the python script. Some additional work is required to make it work without a schema file but correctly supplied values.

### Fixed
- Fixed UID/GID issue which came in with new SuSE image on May 23rd by changing the default UID to 900. UID remains automatic unless specified
- Changed the order of the deployment to fix bugs introduced by GSDK being removed from the SLES images on May 23rd
- Added '-quiet' flag to logging functions so the deployments won't fail if there is a problem writing the logs (e.g, Stackdriver Logging API isn't enabled)

----

## [3.0] 2018-06-04
### Added
- Released sap_hana_ha Linux template & associated functions.
- Released sap_ase Windows template & associated functions
- Released sap_ase Linux template & associated functions