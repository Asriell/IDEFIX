from Pixel import Pixel
import time


class Region:

    """
    id
    r, g, b (sums of all members pixels)
    size
    """

    def __init__(self, id_reg):
        self.r = 0
        self.g = 0
        self.b = 0
        self.id = id_reg
        self.size = 0
        self.neighbors = []

    def get_true_id(self, given_id, regions):
        if self.id == given_id:
            return self.id
        else:
            self.id = regions[self.id].get_true_id(self.id, regions)
            return self.id

    def get_average(self):
        return [self.r / self.size, self.g / self.size, self.b / self.size]

    def add_pixel(self, pix):
        self.r += pix.r()
        self.g += pix.g()
        self.b += pix.b()
        self.size += 1
        pix.reg_id = self.id
        pix.color = 2

    def diff(self, pix):
        """
        Returns the difference between the given pixel and the region.
        :param pix:
            A pixel to compare to the region.
        :return int:
        """
        return max(abs(pix.r() - (self.r / self.size)),
                   abs(pix.g() - (self.g / self.size)),
                   abs(pix.b() - (self.b / self.size)))

    def diff_region(self, r, tolerance):
        if max(abs(self.r / self.size - r.r / r.size),
               abs(self.g / self.size - r.g / r.size),
               abs(self.b / self.size - r.b / r.size)) < tolerance:
            return True
        return False

    def diff_region_value(self, r):
        return max(abs(self.r / self.size - r.r / r.size),
                   abs(self.g / self.size - r.g / r.size),
                   abs(self.b / self.size - r.b / r.size))

    def acceptable(self, pixel, tolerance):
        red = self.r / self.size
        green = self.g / self.size
        blue = self.b / self.size
        if max(abs(red - pixel.r()),
               abs(green - pixel.g()),
               abs(blue - pixel.b())) < tolerance:
            return True
        return False

    def add_neighbors(self, pixel):
        if (pixel.reg_id != -1) and (pixel.reg_id != self.id) and (pixel.reg_id not in self.neighbors):
            self.neighbors.append(pixel.reg_id)


class PixMap:

    """
    queue
    pm (pixel map)
    regions
    width (width of the image)
    """

    def __init__(self):
        self.queue = []
        self.pm = []
        self.width = 0
        self.regions = []
        self.tolerance = 20
        self.number_of_regions = 0
        self.processed = []

    def clear(self):
        """
        Reset the class.
        :return void:
        """
        self.queue = []
        self.pm = []
        self.width = 0
        self.regions = []

    def edge_segmentation(self):
        for pix in self.pm:
            for link in pix.link:
                if not self.pm[link].is_edge and not pix.acceptable(self.pm[link], self.tolerance):
                    pix.col_pix.r = 0
                    pix.col_pix.g = 0
                    pix.col_pix.b = 0
                    pix.is_edge = True
                    break
        for pix in self.pm:
            if pix.r() > 0 and pix.g() > 0 and pix.b() > 0:
                pix.col_pix.r = 255
                pix.col_pix.g = 255
                pix.col_pix.b = 255

    def edge_segmentation_after_reg_growing(self):
        """
        Detect borders. To use only after the region growing.
        :return void:
        """
        for pix in self.pm:
            for link in pix.link:
                if not self.pm[link].is_edge and pix.reg_id != self.pm[link].reg_id:
                    pix.col_pix.r = 0
                    pix.col_pix.g = 0
                    pix.col_pix.b = 0
                    pix.is_edge = True
                    break

    def fill_with_regions(self):
        for pix in self.pm:
            pix.col_pix.r = self.regions[pix.reg_id].get_average()[0]
            pix.col_pix.g = self.regions[pix.reg_id].get_average()[1]
            pix.col_pix.b = self.regions[pix.reg_id].get_average()[2]

    def set_tolerance(self, value):
        self.tolerance = value

    def set_number_of_regions(self, value):
        self.number_of_regions = value

    def feed(self, raw_input):
        """
        Initialize the pixmap with an array of pixels.
        :return void:
        :parameter
            raw_input: array[L][C] of pixels [r, g, b]
        """
        y = 0
        self.width = raw_input.__len__()
        for i in raw_input:
            x = 0
            for j in i:
                p = Pixel()

                # set id
                p.id = i.__len__() * y + x

                # adding links 4-connect
                if x - 1 >= 0:
                    p.add_link(i.__len__() * y + x - 1)
                if x + 1 < i.__len__():
                    p.add_link(i.__len__() * y + x + 1)
                if y - 1 >= 0:
                    p.add_link(i.__len__() * (y - 1) + x)
                if y + 1 < raw_input.__len__():
                    p.add_link(i.__len__() * (y + 1) + x)
                # ----

                # adding links 8-connect

                if x - 1 >= 0 and y - 1 >= 0:
                    p.add_link(i.__len__() * (y - 1) + x - 1)
                if x + 1 < i.__len__() and y - 1 >= 0:
                    p.add_link(i.__len__() * (y - 1) + x + 1)
                if y + 1 < raw_input.__len__() and x + 1 < i.__len__():
                    p.add_link(i.__len__() * (y + 1) + x + 1)
                if y + 1 < raw_input.__len__() and x - 1 >= 0:
                    p.add_link(i.__len__() * (y + 1) + x - 1)
                # ----

                # set color
                p.col_pix.r = j[0]
                p.col_pix.g = j[1]
                p.col_pix.b = j[2]

                self.pm.append(p)

                x += 1
            y += 1

    def reg_merging(self):
        """
        Merge the regions created after the region growing algorithm.
        :return void:
        """
        t1 = time.time_ns()
        initial_count = self.regions.__len__()
        for pix in self.pm:
            for li in pix.link:
                self.regions[pix.reg_id].add_neighbors(self.pm[li])
        for reg in self.regions:
            sorted(reg.neighbors, key=lambda k: reg.diff_region_value(self.regions[k]))
            for merge in self.regions:
                if (reg.id in merge.neighbors or merge.id in reg.neighbors) and reg.id != merge.id:
                    if reg.diff_region(merge, self.tolerance)\
                            or (merge.size < 500 and merge.id == reg.neighbors[0]):
                        reg.r += merge.r
                        reg.g += merge.g
                        reg.b += merge.b
                        reg.size += merge.size

                        merge.r = reg.r
                        merge.g = reg.g
                        merge.b = reg.b
                        merge.size = reg.size

                        if reg.id < merge.id:
                            merge.id = reg.id
                        else:
                            reg.id = merge.id
        final_reg = []
        """for reg in self.regions:
            if reg.neighbors.__len__() == 1:
                reg.id = self.regions[reg.neighbors[0]].id
                # reg = self.regions[reg.neighbors[0]]"""
        """old_region = self.regions
        for reg in self.regions:
            reg.id = reg.get_true_id(reg.id, self.regions)
        while old_region != self.regions:
            old_region = self.regions
            for reg in self.regions:
                reg.id = reg.get_true_id(reg.id, self.regions)
        for reg in self.regions:
            if reg.id not in final_reg:
                final_reg.append(reg.id)"""
        print("Reduce regions from " + str(initial_count) + " to " + str(final_reg.__len__()))
        print("Merging: " + str((time.time_ns() - t1) / 1000000) + "ms")

    def reg_growing_v2(self):
        """
        Implements the region growing algorithm.
        :return void:
        """
        t1 = time.time_ns()
        self.processed = []
        pixel_index = 0
        while self.processed.__len__() != self.pm.__len__():
            new_reg = Region(self.regions.__len__())
            while self.pm[pixel_index].color != 0:
                pixel_index += 1
            new_reg.add_pixel(self.pm[pixel_index])
            self.regions.append(new_reg)
            self.queue.append(pixel_index)
            while self.queue.__len__() > 0:
                self.select_current(self.regions[-1])
        print("Growing: " + str((time.time_ns() - t1) / 1000000) + "ms")

    def add_to_queue(self, pixel_id):
        """
        Add a pixel to the queue, checking if it's legit or not.
        :param pixel_id:
        :return void:
        """
        if self.pm[pixel_id].color == 0:
            self.queue.append(pixel_id)
            self.pm[pixel_id].color = 1

    def select_current(self, region):
        """
        Select the best pixel and add it to a region (removing it from the queue at the same time).
        :return void:
        """
        current = self.queue[0]
        region.add_pixel(self.pm[current])
        self.processed.append(current)
        for linked_pixel in self.pm[current].link:
            """if region.acceptable(self.pm[linked_pixel], self.tolerance):"""
            if self.pm[current].acceptable(self.pm[linked_pixel], self.tolerance):
                if self.pm[linked_pixel].color != 0:
                    self.regions[self.pm[current].reg_id].add_neighbors(self.pm[linked_pixel])
                self.add_to_queue(linked_pixel)
        self.queue.pop(0)

    def signal_segmentation(self):
        reg_id = 0
        limit_value = 25
        for y in range(int(self.pm.__len__() / self.width)):
            points = []
            yw = y * self.width
            for x in range(self.width):
                points.append(self.pm[yw + x - 1].average())
                self.pm[yw + x - 1].is_edge = False
            dx = []
            dx_copy = []
            for i in range(points.__len__() - 1):
                if i > 0:
                    dx.append((points[i + 1] - points[i - 1]) / 2)
                    dx_copy.append((points[i + 1] - points[i - 1]) / 2)
                    if abs(dx[-1]) < limit_value:
                        dx[-1] = 0
                else:
                    dx.append(0)
                    dx_copy.append(0)
            self.pm[yw].reg_id = reg_id
            for x in range(self.width - 2):
                if abs(dx[x - 1]) < abs(dx[x]) and abs(dx[x]) > abs(dx[x + 1]):
                    reg_id += 1
                self.pm[yw + x].reg_id = reg_id
                self.pm[yw + x].is_edge = True
            self.pm[yw + self.width - 1].reg_id = reg_id

        return reg_id

    def signal_segmentation_lining(self):
        for y in range(int(self.pm.__len__() / self.width)):
            yw = y * self.width
            for x in range(self.width):
                if self.pm[yw + x].r() == 0:
                    self.pm[yw + x].is_edge = True
                else:
                    self.pm[yw + x].is_edge = False
        for y in range(int(self.pm.__len__() / self.width) - 2):
            yw = (y + 1) * self.width
            for x_at_zero in range(self.width - 2):
                x = x_at_zero + 1
                if self.pm[yw + x].is_edge:
                    for i in [yw - self.width, yw, yw + self.width]:
                        for j in [x - 1, x, x + 1]:
                            tmp_y = -i + yw
                            tmp_x = -j + x
                            if self.pm[i + j].is_edge and not self.pm[tmp_y + tmp_x].is_edge:
                                self.pm[tmp_y + yw + tmp_x + x].potential = True
                                self.pm[tmp_y + yw + tmp_x + x].is_edge = True
