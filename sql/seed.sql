-- ============================================
-- 初始数据：鸟类百科 + 测试用户
-- ============================================

USE bird_watching;

-- 插入鸟类数据（Top 10 常见鸟类）
INSERT INTO birds (name, latin_name, region, habits, description, image_url, search_count) VALUES
('麻雀', 'Passer montanus', '全国广泛分布', '群居，适应力强，常在建筑物周围活动', '最常见的城市鸟类之一，体型小巧，灰褐色羽毛', 'https://example.com/images/sparrow.jpg', 1520),
('喜鹊', 'Pica pica', '全国广泛分布', '留鸟，常成对或小群活动，杂食性', '黑白色羽毛，尾长，叫声响亮，被认为是吉祥鸟', 'https://example.com/images/magpie.jpg', 1280),
('燕子', 'Hirundo rustica', '全国广泛分布', '候鸟，春季飞来秋季南迁，在屋檐下筑巢', '飞行速度快，尾羽分叉如剪刀，捕食昆虫', 'https://example.com/images/swallow.jpg', 980),
('啄木鸟', 'Dendrocopos major', '东北、华北、华南', '独居，在树干上凿洞觅食，以昆虫为食', '森林医生，强有力的喙可啄开树皮', 'https://example.com/images/woodpecker.jpg', 750),
('翠鸟', 'Alcedo atthis', '南方水域常见', '栖息于水边，俯冲捕鱼，飞行速度快', '羽毛翠蓝鲜艳，小型鸟类，以鱼类为食', 'https://example.com/images/kingfisher.jpg', 620),
('白鹭', 'Egretta garzetta', '南方湿地、水田', '涉禽，在浅水中觅食鱼虾，常成群活动', '全身白色羽毛，姿态优雅，常见于水边', 'https://example.com/images/egret.jpg', 540),
('猫头鹰', 'Strigiformes', '全国山区林地', '夜行性，白天栖息在树洞中，以鼠类为食', '面部似猫，眼睛大而圆，是夜间捕猎能手', 'https://example.com/images/owl.jpg', 480),
('黄鹂', 'Oriolus chinensis', '东部、南部地区', '树栖性，叫声清脆悦耳，以昆虫为食', '羽毛金黄亮丽，鸣声婉转动听，夏季繁殖', 'https://example.com/images/oriole.jpg', 390),
('画眉', 'Garrulax canorus', '华南、西南地区', '栖息于灌丛中，善鸣叫，领域性强', '眼圈白色如画眉，鸣声多变悦耳，著名笼养鸟', 'https://example.com/images/thrush.jpg', 310),
('丹顶鹤', 'Grus japonensis', '东北地区（繁殖）', '候鸟，栖息于湿地沼泽，以鱼虾为食', '头顶红色肉冠，姿态优雅，中国传统文化吉祥鸟', 'https://example.com/images/crane.jpg', 280),
('鸳鸯', 'Aix galericulata', '东北、华北、南方越冬', '候鸟，喜在水边活动，成对出现', '羽毛色彩艳丽，雌雄异色，象征爱情', 'https://example.com/images/mandarin_duck.jpg', 260),
('杜鹃', 'Cuculus canorus', '全国广泛分布', '候鸟，叫声"布谷"二声，巢寄生繁殖', '灰褐色羽毛，春夏之交鸣叫，催促农耕', 'https://example.com/images/cuckoo.jpg', 230),
('天鹅', 'Cygnus', '北方湖泊湿地', '候鸟，群居，优雅的游泳姿态', '大型水禽，颈长，羽毛洁白，迁徙时成V字形', 'https://example.com/images/swan.jpg', 210),
('孔雀', 'Pavo cristatus', '云南、东南亚', '栖息于海拔较低的山地森林', '雄鸟尾屏华丽，开屏时极为壮观，观赏鸟类', 'https://example.com/images/peacock.jpg', 190);

-- 插入测试用户（密码都是: 123456）
INSERT INTO users (username, password_hash, nickname, avatar, bio) VALUES
('testuser', '$2b$12$LJ3m4ys3Lk0TSwHpsNgOjeK1mPmVEpMCEfY/hHqZOcOv6gHvPBq.', '测试用户', '', '一个观鸟爱好者'),
('birdfan', '$2b$12$LJ3m4ys3Lk0TSwHpsNgOjeK1mPmVEpMCEfY/hHqZOcOv6gHvPBq.', '观鸟达人', '', '热爱自然，热爱鸟类'),
('admin', '$2b$12$LJ3m4ys3Lk0TSwHpsNgOjeK1mPmVEpMCEfY/hHqZOcOv6gHvPBq.', '管理员', '', '系统管理员');

-- 插入测试帖子
INSERT INTO posts (user_id, title, content, images, location) VALUES
(1, '今天在公园拍到一只翠鸟', '在莲花山公园蹲守了一上午，终于拍到翠鸟捕鱼的精彩瞬间！', '["https://example.com/images/post1.jpg"]', '深圳莲花山公园'),
(1, '深圳湾的候鸟季开始了', '每年这个时候都能看到大量的候鸟在深圳湾栖息，场面非常壮观。推荐大家带望远镜来观鸟！', '["https://example.com/images/post2.jpg"]', '深圳湾公园'),
(2, '新手观鸟必备装备推荐', '作为一个观鸟三年的爱好者，今天给大家分享一下入门观鸟需要准备哪些装备。', '[]', ''),
(2, '今天在野外发现猫头鹰巢穴', '在一棵老榕树上发现了一个猫头鹰的巢穴，里面还有两只幼鸟，太可爱了！', '["https://example.com/images/post3.jpg"]', '白云山');

-- 插入测试评论
INSERT INTO comments (post_id, user_id, content) VALUES
(1, 2, '翠鸟拍得真清楚！用的什么镜头？'),
(1, 3, '莲花山公园确实是个观鸟的好地方'),
(2, 1, '今年好像比往年来得早些'),
(3, 1, '收藏了，准备入坑观鸟！');
