-- MySQL dump 10.13  Distrib 9.0.1, for macos15.1 (arm64)
--
-- Host: localhost    Database: poker_db
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `game_history`
--

DROP TABLE IF EXISTS `game_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `session_id` varchar(50) DEFAULT NULL,
  `screenshot_path` varchar(255) DEFAULT NULL,
  `game_state` json DEFAULT NULL,
  `player_cards` varchar(10) DEFAULT NULL,
  `board_cards` varchar(20) DEFAULT NULL,
  `position` varchar(10) DEFAULT NULL,
  `pot_size` decimal(10,2) DEFAULT NULL,
  `action_taken` varchar(20) DEFAULT NULL,
  `action_amount` decimal(10,2) DEFAULT NULL,
  `ai_decision` text,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `game_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_history`
--

LOCK TABLES `game_history` WRITE;
/*!40000 ALTER TABLE `game_history` DISABLE KEYS */;
INSERT INTO `game_history` VALUES (1,1,'test_session','poker_captures/poker_table_20250101_204545.png','{\"stage\": \"preflop\", \"position\": \"BB\", \"pot_size\": 1.0, \"hand_cards\": [\"3s\", \"2h\"], \"current_bet\": 0.0, \"player_stacks\": {\"Lulu-Tim\": 49.0, \"dalun_tw\": 94.1, \"LilShady68\": 99.3, \"Fishy player\": 100.0, \"MONEYCOMEIN!\": 99.3, \"wanyu20020824\": 101.2}, \"community_cards\": []}','3s 2h','','BB',1.00,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"3s\", \"2h\"]}}','2025-01-01 12:45:53'),(2,1,'test_session','poker_captures/poker_table_20250101_215000.png','{\"stage\": \"preflop\", \"position\": \"BB\", \"pot_size\": 2.5, \"hand_cards\": [\"K♦\", \"8♦\"], \"current_bet\": 0.0, \"player_stacks\": {\"JarilKK\": 154.5, \"e958744\": 158.8, \"Lulu-Tim\": 112.1, \"dalun_tw\": 95.1, \"JasperChi\": 159.8, \"Fishy player\": 79.2, \"wanyu20020824\": 153.9}, \"community_cards\": []}','K♦ 8♦','','BB',2.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"K\\u2666\", \"8\\u2666\"]}}','2025-01-01 13:50:06'),(3,1,'test_session','poker_captures/poker_table_20250101_215448.png','{\"stage\": \"preflop\", \"position\": \"MP\", \"pot_size\": 2.5, \"hand_cards\": [\"3h\", \"6d\"], \"current_bet\": 0.0, \"player_stacks\": {\"JarIKK\": 148.2, \"e958744\": 154.3, \"Lulu-Tim\": 111.1, \"aklamlam\": 95.0, \"dalun_tw\": 95.9, \"JasperChi\": 172.6, \"Fishy player\": 79.2}, \"community_cards\": []}','3h 6d','','MP',2.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"3h\", \"6d\"]}}','2025-01-01 13:54:54'),(4,1,'test_session','poker_captures/poker_table_20250101_224133.png','{\"stage\": \"preflop\", \"position\": \"BTN\", \"pot_size\": 2.5, \"hand_cards\": [\"A♠\", \"9♠\"], \"current_bet\": 0.0, \"player_stacks\": {\"JarilKK\": 223.1, \"Lulu-Tim\": 102.0, \"dalun_tw\": 132.3, \"Fishy player\": 81.8}, \"community_cards\": []}','A♠ 9♠','','BTN',2.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"A\\u2660\", \"9\\u2660\"]}}','2025-01-01 14:41:39'),(5,1,'test_session','poker_captures/poker_table_20250101_225000.png','{\"stage\": \"preflop\", \"position\": \"BTN\", \"pot_size\": 2.5, \"hand_cards\": [\"K♠\", \"6♥\"], \"current_bet\": 0.0, \"player_stacks\": {\"Lulu-Tim\": 98.0, \"dalun_tw\": 139.0, \"Pasha Paradox\": 99.0}, \"community_cards\": []}','K♠ 6♥','','BTN',2.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"K\\u2660\", \"6\\u2665\"]}}','2025-01-01 14:50:06'),(8,1,'test_session','poker_captures/poker_table_20250101_225852.png','{\"stage\": \"preflop\", \"position\": \"BTN\", \"pot_size\": 4.5, \"hand_cards\": [\"6c\", \"4c\"], \"current_bet\": 0.0, \"player_stacks\": {\"Kei_kei\": 97.1, \"Durrrrwe\": 101.5, \"Lulu-Tim\": 88.7, \"dalun_tw\": 129.4, \"Pasha Paradox\": 103.2, \"nobadbeatplzz\": 98.5, \"PayMonyToMyCard\": 114.2}, \"community_cards\": []}','6c 4c','','BTN',4.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"6c\", \"4c\"]}}','2025-01-01 14:58:59'),(9,1,'test_session','poker_captures/poker_table_20250101_230609.png','{\"stage\": \"preflop\", \"position\": \"BB\", \"pot_size\": 1.5, \"hand_cards\": [\"4s\", \"Ah\"], \"current_bet\": 0.0, \"player_stacks\": {\"Kei_kei\": 37.3, \"Durrrrwe\": 138.5, \"Lulu-Tim\": 87.2, \"FieldsNiel\": 89.0, \"FiShErMaN1212\": 49.0, \"Pasha Paradox\": 101.7, \"nobadbeatplzz\": 99.5}, \"community_cards\": []}','4s Ah','','BB',1.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"4s\", \"Ah\"]}}','2025-01-01 15:06:16'),(10,1,'test_session','poker_captures/poker_table_20250101_231111.png','{\"stage\": \"preflop\", \"position\": \"SB\", \"pot_size\": 1.5, \"hand_cards\": [\"Qh\", \"Jh\"], \"current_bet\": 0.0, \"player_stacks\": {\"Kei_kei\": 26.9, \"Durrrrwe\": 148.5, \"Lulu-Tim\": 85.7, \"FieldsNiel\": 83.5, \"Pasha Paradox\": 101.7, \"nobadbeatplzz\": 104.7, \"wanyu20020824\": 100.0}, \"community_cards\": []}','Qh Jh','','SB',1.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"Qh\", \"Jh\"]}}','2025-01-01 15:11:18'),(11,1,'test_session','poker_captures/poker_table_20250101_231132.png','{\"stage\": \"flop\", \"position\": \"CO\", \"pot_size\": 3.5, \"hand_cards\": [\"Qd\", \"Jh\"], \"current_bet\": 0.0, \"player_stacks\": {\"Kei_kei\": 26.9, \"Lulu-Tim\": 84.7, \"FieldsNiel\": 82.5, \"Pasha Paradox\": 101.7, \"nobadbeatplzz\": 104.7, \"wanyu20020824\": 100.0}, \"community_cards\": [\"Kd\", \"6d\", \"6c\"]}','Qd Jh','Kd 6d 6c','CO',3.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"flop\", \"cards\": {\"community\": [\"Kd\", \"6d\", \"6c\"], \"hand\": [\"Qd\", \"Jh\"]}}','2025-01-01 15:11:40'),(12,1,'test_session','poker_captures/poker_table_20250101_232638.png','{\"stage\": \"preflop\", \"position\": \"CO\", \"pot_size\": 4.5, \"hand_cards\": [\"7c\", \"Qc\"], \"current_bet\": 0.0, \"player_stacks\": {\"Lulu-Tim\": 76.9, \"Jocksiuuu\": 138.4, \"Squareuuu\": 100.0, \"FieldsNiel\": 94.7, \"Pasha Paradox\": 113.4, \"nobadbeatplzz\": 137.3, \"wanyu20020824\": 99.0}, \"community_cards\": []}','7c Qc','','CO',4.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"7c\", \"Qc\"]}}','2025-01-01 15:26:45'),(13,1,'test_session','poker_captures/poker_table_20250101_233251.png','{\"stage\": \"preflop\", \"position\": \"BB\", \"pot_size\": 1.5, \"hand_cards\": [\"7c\", \"3c\"], \"current_bet\": 0.0, \"player_stacks\": {\"Lulu-Tim\": 71.9, \"Jocksiuuu\": 135.4, \"Squareuuu\": 107.6, \"FieldsNiel\": 111.4, \"Pasha Paradox\": 109.4, \"nobadbeatplzz\": 141.9, \"wanyu20020824\": 99.5}, \"community_cards\": []}','7c 3c','','BB',1.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"7c\", \"3c\"]}}','2025-01-01 15:32:59'),(14,1,'test_session','poker_captures/poker_table_20250101_235251.png','{\"stage\": \"preflop\", \"position\": \"BB\", \"pot_size\": 1.5, \"hand_cards\": [\"9d\", \"6d\"], \"current_bet\": 0.0, \"player_stacks\": {\"Ping527\": 69.9, \"Lulu-Tim\": 82.5, \"Jocksluuu\": 153.2, \"FieldsNiel\": 96.5, \"Pasha Paradox\": 128.4, \"nobadbeatplzz\": 157.5, \"wanyu20020824\": 108.2}, \"community_cards\": []}','9d 6d','','BB',1.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"9d\", \"6d\"]}}','2025-01-01 15:52:58'),(15,1,'test_session','poker_captures/poker_table_20250101_235752.png','{\"stage\": \"preflop\", \"position\": \"SB\", \"pot_size\": 3.5, \"hand_cards\": [\"10c\", \"2c\"], \"current_bet\": 0.0, \"player_stacks\": {\"Ping527\": 69.9, \"Lulu-Tim\": 77.0, \"Jocksiuuu\": 136.0, \"FieldsNiel\": 99.8, \"Martin0206\": 99.0, \"Pasha Paradox\": 120.8, \"wanyu20020824\": 117.9}, \"community_cards\": []}','10c 2c','','SB',3.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"10c\", \"2c\"]}}','2025-01-01 15:57:59'),(16,1,'test_session','poker_captures/poker_table_20250102_000034.png','{\"stage\": \"preflop\", \"position\": \"BTN\", \"pot_size\": 3.5, \"hand_cards\": [\"7d\", \"4d\"], \"current_bet\": 0.0, \"player_stacks\": {\"Ping527\": 75.2, \"Lulu-Tim\": 77.0, \"FieldsNiel\": 103.1, \"Martin0206\": 91.7, \"Pasha Paradox\": 120.3, \"The right one\": 46.5, \"wanyu20020824\": 108.4}, \"community_cards\": []}','7d 4d','','BTN',3.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"7d\", \"4d\"]}}','2025-01-01 16:00:42'),(17,1,'test_session','poker_captures/poker_table_20250102_143301.png','{\"stage\": \"preflop\", \"position\": \"SB\", \"pot_size\": 2.5, \"hand_cards\": [\"Ks\", \"Tc\"], \"current_bet\": 0.0, \"player_stacks\": {\"lyq111\": 42.1, \"HUH G19\": 96.6, \"ron0927\": 99.0, \"Lulu-Tim\": 49.0, \"lowroller\": 58.0, \"LilShady68\": 159.5, \"P9322-6844\": 269.6}, \"community_cards\": []}','Ks Tc','','SB',2.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"Ks\", \"Tc\"]}}','2025-01-02 06:33:10'),(18,1,'test_session','poker_captures/poker_table_20250102_143314.png','{\"stage\": \"flop\", \"position\": \"BB\", \"pot_size\": 3.0, \"hand_cards\": [\"Ks\", \"Kd\", \"10s\"], \"current_bet\": 0.0, \"player_stacks\": {\"lyq111\": 41.6, \"HUH G19\": 96.6, \"ron0927\": 99.0, \"Lulu-Tim\": 49.0, \"lowroller\": 58.0, \"LilShady68\": 159.5, \"P9322-6844\": 269.6}, \"community_cards\": [\"Kc\", \"Qh\", \"8h\"]}','Ks Kd 10s','Kc Qh 8h','BB',3.00,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"flop\", \"cards\": {\"community\": [\"Kc\", \"Qh\", \"8h\"], \"hand\": [\"Ks\", \"Kd\", \"10s\"]}}','2025-01-02 06:33:22'),(19,1,'test_session','poker_captures/poker_table_20250102_143933.png','{\"stage\": \"preflop\", \"position\": \"BTN\", \"pot_size\": 2.0, \"hand_cards\": [\"K4\", \"(方塊)\"], \"current_bet\": 0.0, \"player_stacks\": {\"lyq111\": 13.8, \"HUH G19\": 95.1, \"ron0927\": 126.3, \"Lulu-Tim\": 53.4, \"lowroller\": 56.5, \"LilShady68\": 155.0, \"P9322-6844\": 270.2}, \"community_cards\": []}','K4 (方塊)','','BTN',2.00,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"K4\"]}}','2025-01-02 06:39:41'),(20,1,'test_session','poker_captures/poker_table_20250102_144144.png','{\"stage\": \"flop\", \"position\": \"NA\", \"pot_size\": 3.0, \"hand_cards\": [\"T9s\", \"(可見)\"], \"current_bet\": 0.0, \"player_stacks\": {\"lyq111\": 13.8, \"HUH G19\": 95.1, \"ron0927\": 126.3, \"Lulu-Tim\": 51.4, \"lowroller\": 55.5, \"LilShady68\": 134.2, \"P9322-6844\": 290.5}, \"community_cards\": [\"Js\", \"Qs\", \"8s\"]}','T9s (可見)','Js Qs 8s','NA',3.00,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"flop\", \"cards\": {\"community\": [\"Js\", \"Qs\", \"8s\"], \"hand\": [\"T9s\"]}}','2025-01-02 06:41:52'),(21,1,'test_session','poker_captures/poker_table_20250102_145039.png','{\"stage\": \"preflop\", \"position\": \"BB\", \"pot_size\": 1.5, \"hand_cards\": [\"4h\", \"5d\"], \"current_bet\": 0.0, \"player_stacks\": {\"xunz20\": 100.0, \"HUH G19\": 79.1, \"Lulu-Tim\": 100.4, \"lowroller\": 53.5, \"LilShady68\": 144.8, \"P9322-6844\": 274.1, \"Qpalzm9045\": 119.2}, \"community_cards\": []}','4h 5d','','BB',1.50,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"preflop\", \"cards\": {\"community\": [], \"hand\": [\"4h\", \"5d\"]}}','2025-01-02 06:50:47'),(22,1,'test_session','poker_captures/poker_table_20250102_145523.png','{\"stage\": \"flop\", \"position\": \"BTN\", \"pot_size\": 7.0, \"hand_cards\": [\"Kc\", \"Qc\"], \"current_bet\": 0.0, \"player_stacks\": {\"Sevenr\": 50.0, \"xunz20\": 110.6, \"HUH G19\": 79.1, \"Lulu-Tim\": 94.0, \"lowroller\": 51.5, \"LilShady68\": 139.3, \"P9322-6844\": 270.6}, \"community_cards\": [\"9d\", \"9s\", \"5c\"]}','Kc Qc','9d 9s 5c','BTN',7.00,'fold',0.00,'{\"action\": \"fold\", \"amount\": 0, \"stage\": \"flop\", \"cards\": {\"community\": [\"9d\", \"9s\", \"5c\"], \"hand\": [\"Kc\", \"Qc\"]}}','2025-01-02 06:55:31'),(23,1,'test_session','poker_captures/poker_table_20250102_151038.png','{\"stage\": \"preflop (無公共牌)\", \"position\": \"\", \"pot_size\": 2.5, \"hand_cards\": [\"K♦\", \"5♦\"], \"current_bet\": 0.0, \"player_stacks\": {\"Sevenr\": 64.6, \"xunz20\": 103.2, \"HUH G19\": 76.6, \"Lulu-Tim\": 47.0, \"lowroller\": 28.1, \"P9322-6844\": 266.9, \"B@ronFullHousen\": 100.0}, \"community_cards\": [\"尚未發牌\"]}','K♦ 5♦','尚未發牌','',2.50,'raise',2.00,'{\"action\": \"raise\", \"amount\": 2.0, \"stage\": \"preflop\", \"cards\": {\"community\": [\"\\u5c1a\\u672a\\u767c\\u724c\"], \"hand\": [\"K\\u2666\", \"5\\u2666\"]}}','2025-01-02 07:10:48');
/*!40000 ALTER TABLE `game_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'timwei','chwei9181@gmail.com','$2a$10$41YKRy79j2AIgrPZLbRpy.CO4CeKNrD8LVLt3sO8Q3TKi2eNncucK','2024-12-26 20:25:43'),(2,'Wei','brandy.cohort_9j@icloud.com','$2a$10$Plelj/RXNLkyKazreM1o1OeMJi5u86udzI4Gqh0fs3am3QSAwmQvC','2025-01-01 09:28:02');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-08  2:26:38
