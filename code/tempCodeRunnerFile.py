  # folders = list(walk(join('images', 'enemies')))[0][1]
        # self.enemy_frames = {}
        # for folder in folders:
        #     for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
        #         self.enemy_frames[folder] = []
        #         for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
        #             full_path = join(folder_path, file_name)
        #             surf = pygame.image.load(full_path).convert_alpha()
        #             self.enemy_frames[folder].append(surf)