-- MySQL Workbench Synchronization
-- Generated: 2019-01-20 23:42
-- Model: New Model
-- Version: 1.0
-- Project: Name of the project
-- Author: Alcides

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `secompufscar` DEFAULT CHARACTER SET utf8 ;

CREATE TABLE IF NOT EXISTS `secompufscar`.`participante` (
  `id` INT(11) NOT NULL,
  `usuario_id` INT(11) NOT NULL,
  `edicao` INT(4) NOT NULL,
  `pacote` TINYINT(1) NOT NULL,
  `pagamento` TINYINT(1) NULL DEFAULT NULL,
  `camiseta` VARCHAR(3) NULL DEFAULT NULL,
  `data_inscricao` DATE NOT NULL,
  `credenciado` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`, `usuario_id`),
  INDEX `fk_participante_usuario_idx` (`usuario_id` ASC),
  CONSTRAINT `fk_participante_usuario`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `secompufscar`.`usuario` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `secompufscar`.`usuario` (
  `id` INT(11) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `senha` VARCHAR(256) NOT NULL,
  `ultimo_login` VARCHAR(45) NOT NULL,
  `data_cadastro` DATE NOT NULL,
  `permissao` INT(1) NOT NULL,
  `primeiro_nome` VARCHAR(45) NOT NULL,
  `ult_nome` VARCHAR(45) NOT NULL,
  `curso` VARCHAR(45) NOT NULL,
  `cidade` VARCHAR(45) NOT NULL,
  `instituicao` VARCHAR(45) NOT NULL,
  `token_email` VARCHAR(90) NOT NULL,
  `data_nasc` DATE NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `secompufscar`.`atividade` (
  `y` INT(11) NOT NULL,
  PRIMARY KEY (`y`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `secompufscar`.`presenca` (
  `participante_id` INT(11) NOT NULL,
  `participante_usuario_id` INT(11) NOT NULL,
  `atividade_y` INT(11) NOT NULL,
  PRIMARY KEY (`participante_id`, `participante_usuario_id`, `atividade_y`),
  INDEX `fk_presenca_atividade1_idx` (`atividade_y` ASC),
  CONSTRAINT `fk_presenca_participante1`
    FOREIGN KEY (`participante_id` , `participante_usuario_id`)
    REFERENCES `secompufscar`.`participante` (`id` , `usuario_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_presenca_atividade1`
    FOREIGN KEY (`atividade_y`)
    REFERENCES `secompufscar`.`atividade` (`y`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `secompufscar`.`inscricao` (
  `participante_id` INT(11) NOT NULL,
  `participante_usuario_id` INT(11) NOT NULL,
  `atividade_y` INT(11) NOT NULL,
  PRIMARY KEY (`participante_id`, `participante_usuario_id`, `atividade_y`),
  INDEX `fk_presenca_atividade1_idx` (`atividade_y` ASC),
  CONSTRAINT `fk_presenca_participante10`
    FOREIGN KEY (`participante_id` , `participante_usuario_id`)
    REFERENCES `secompufscar`.`participante` (`id` , `usuario_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_presenca_atividade10`
    FOREIGN KEY (`atividade_y`)
    REFERENCES `secompufscar`.`atividade` (`y`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

