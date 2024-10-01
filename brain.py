class Brain:
    def __init__(self, holes_weight, blocks_above_holes_weight,pillars_weight, max_height_weight, bumpiness_weight, blocks_in_rightmost_lane_weight):
        # Initialize multipliers for each stat
        self.holes_weight = holes_weight
        self.blocks_above_holes_weight = blocks_above_holes_weight
        self.pillars_weight = pillars_weight
        self.max_height_weight = max_height_weight
        self.bumpiness_weight = bumpiness_weight
        self.blocks_in_rightmost_lane_weight = blocks_in_rightmost_lane_weight

    def compute_weight(self, holes, blocks_above_holes, pillars, max_height, bumpiness, blocks_in_rightmost_lane, lines_cleared):
        weighted_holes = holes * self.holes_weight
        weighted_block_above_holes = blocks_above_holes * self.blocks_above_holes_weight
        weighted_pillars = pillars * self.pillars_weight
        weighted_max_height = max_height * self.max_height_weight
        weighted_bumpiness = bumpiness * self.bumpiness_weight
        weighted_rightmost_blocks = blocks_in_rightmost_lane * self.blocks_in_rightmost_lane_weight

        # Base total weight calculation
        total_weight = (weighted_holes +
                        weighted_pillars +
                        weighted_block_above_holes +
                        weighted_max_height +
                        weighted_bumpiness +
                        weighted_rightmost_blocks)


        if lines_cleared == 4:
            total_weight *= 0.5

        return total_weight


    def adjust_multipliers(self, holes_weight=None, blocks_above_holes_weight=None, pillars_weight=None, max_height_weight=None, bumpiness_weight=None, blocks_in_rightmost_lane_weight=None):
        if holes_weight is not None:
            self.holes_weight = holes_weight
        if blocks_above_holes_weight is not None:
            self.blocks_above_holes_weight = blocks_above_holes_weight
        if pillars_weight is not None:
            self.pillars_weight = pillars_weight
        if max_height_weight is not None:
            self.max_height_weight = max_height_weight
        if bumpiness_weight is not None:
            self.bumpiness_weight = bumpiness_weight
        if blocks_in_rightmost_lane_weight is not None:
            self.blocks_in_rightmost_lane_weight = blocks_in_rightmost_lane_weight

    def print_multipliers(self):
        print(f"Holes weight: {self.holes_weight}")
        print(f"Pillars weight: {self.pillars_weight}")
        print(f"Max height weight: {self.max_height_weight}")
        print(f"Bumpiness weight: {self.bumpiness_weight}")
        print(f"Blocks in rightmost lane weight: {self.blocks_in_rightmost_lane_weight}")
