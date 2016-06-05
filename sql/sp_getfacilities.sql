USE `camping`;
DROP procedure IF EXISTS `sp_GetFacilityNames`;

DELIMITER $$
USE `camping`$$
CREATE PROCEDURE `sp_GetFacilityNames`() 
BEGIN
	select FacilityName from campnear_consolidated;  
END$$

DELIMITER ;
