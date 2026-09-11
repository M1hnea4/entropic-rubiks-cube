#   cd "C:\Users\User\Desktop\Metode avansate"
#   manim -pql cubee.py EntropicRubiksCube


from manim import *
import numpy as np

class EntropicRubiksCube(ThreeDScene):
    def construct(self):
        
        self.N = 30            
        R = 0.05             
        self.cube_size = 3.0    
        self.font_size = 14      
        legend_font_size = 18 
        
        temperature = 0.15   
        velocity_scale = 0.6 
        entropy_bins_per_dim = 2 

        self.max_entropy_per_cube = np.log(entropy_bins_per_dim**3)
        if self.max_entropy_per_cube == 0: 
            self.max_entropy_per_cube = 1.0 

        np.random.seed(1)
      
        self.R = R 
        self.positions = np.random.uniform(-self.cube_size/2 + R, self.cube_size/2 - R, (self.N, 3))
        self.velocities = np.random.normal(scale=velocity_scale, size=(self.N, 3))

        self.sphere_colors = [WHITE, YELLOW, ORANGE, GREEN, BLUE]
        self.sphere_color_indices = np.zeros(self.N, dtype=int)

        sub_cube_size = self.cube_size / 3.0 
        self.rubiks_cube = VGroup()
        self.sub_cube_centers = [] 

        offset = -sub_cube_size 
        
        cube_idx = 0
        for i in range(3): 
            for j in range(3): 
                for k in range(3): 
                    pos = np.array([
                        offset + k * sub_cube_size,
                        offset + j * sub_cube_size,
                        offset + i * sub_cube_size
                    ])
                    self.sub_cube_centers.append(pos)
                    
                    c = Cube(
                        side_length=sub_cube_size, 
                        stroke_width=1.0, 
                        stroke_color=RED, 
                        fill_opacity=0.4, 
                        fill_color=RED  
                    ).move_to(pos)
                    
                    self.rubiks_cube.add(c)
                    cube_idx += 1
        
        self.add(self.rubiks_cube)
        self.sub_cube_centers = np.array(self.sub_cube_centers)

        self.spheres = [
            Sphere(
                radius=R, 
                color=self.sphere_colors[0], 
                resolution=(24, 12) 
            ).move_to(pos) 
            for pos in self.positions
        ]
        self.add(*self.spheres)

        self.set_camera_orientation(phi=65 * DEGREES, theta=45 * DEGREES, zoom=1.5) 
        self.begin_ambient_camera_rotation(rate=0.2) 

        self.current_entropy_display = VGroup()
        self.add_fixed_in_frame_mobjects(self.current_entropy_display)

        legend_red = MarkupText("Red: Low Entropy", font_size=legend_font_size, color=RED)
        legend_blue = MarkupText("Blue: High Entropy", font_size=legend_font_size, color=BLUE)
        
        legend = VGroup(legend_red, legend_blue).arrange(
            DOWN, buff=0.1, aligned_edge=LEFT
        )
        legend.to_corner(DL, buff=0.1) 
        self.add_fixed_in_frame_mobjects(legend)

        def calculate_entropy(particle_positions, sub_cube_center):
            total_particles = len(particle_positions)
            if total_particles <= 1:
                return 0.0 

            num_bins = entropy_bins_per_dim**3 
            bins = np.zeros(num_bins, dtype=int)
            
            bin_size = sub_cube_size / entropy_bins_per_dim
            sub_cube_corner = sub_cube_center - sub_cube_size / 2.0

            for pos in particle_positions:
                local_pos = pos - sub_cube_corner
                bin_x = int(local_pos[0] / bin_size)
                bin_y = int(local_pos[1] / bin_size)
                bin_z = int(local_pos[2] / bin_size)
                
                bin_x = np.clip(bin_x, 0, entropy_bins_per_dim - 1)
                bin_y = np.clip(bin_y, 0, entropy_bins_per_dim - 1)
                bin_z = np.clip(bin_z, 0, entropy_bins_per_dim - 1)
                
                bin_index = bin_x + bin_y * entropy_bins_per_dim + bin_z * (entropy_bins_per_dim**2)
                bins[bin_index] += 1
            
            probabilities = bins[bins > 0] / total_particles
            entropy = -np.sum(probabilities * np.log(probabilities))
            
            return entropy

        def resolve_wall_collisions(positions, velocities):
            for i in range(self.N): 
                for dim in range(3):
                    limit = self.cube_size/2 - self.R 
                    
                    collision = False
                    if positions[i, dim] < -limit:
                        positions[i, dim] = -limit
                        velocities[i, dim] *= -1
                        collision = True
                        
                    elif positions[i, dim] > limit:
                        positions[i, dim] = limit
                        velocities[i, dim] *= -1
                        collision = True
                    
                    if collision:
                        current_index = self.sphere_color_indices[i]
                        new_index = (current_index + 1) % len(self.sphere_colors)
                        self.sphere_color_indices[i] = new_index
                        
                        new_sphere_color = self.sphere_colors[new_index]
                        self.spheres[i].set_style(
                            fill_color=new_sphere_color, 
                            stroke_color=new_sphere_color
                        )
                        # ----------------------------------------

        def resolve_pairwise_collisions(positions, velocities):
            for i in range(self.N):
                for j in range(i+1, self.N):
                    rij = positions[j] - positions[i]
                    dist = np.linalg.norm(rij)
                    if dist < 2*self.R and dist > 1e-8: 
                        n = rij / dist 
                        overlap = 2*self.R - dist
                        positions[i] -= 0.5 * overlap * n
                        positions[j] += 0.5 * overlap * n
                        vi, vj = velocities[i], velocities[j]
                        vi_n = np.dot(vi, n)
                        vj_n = np.dot(vj, n)
                        velocities[i] += (vj_n - vi_n) * n
                        velocities[j] += (vi_n - vj_n) * n

        def update_scene(mob, dt):
            substeps = 5
            dt_sub = dt / substeps
            
            for _ in range(substeps):
                self.velocities += np.random.normal(scale=np.sqrt(2*temperature*dt_sub), size=(self.N,3))
                self.positions += self.velocities * dt_sub
                resolve_wall_collisions(self.positions, self.velocities)
                resolve_pairwise_collisions(self.positions, self.velocities)
            
            for s, p in zip(self.spheres, self.positions):
                s.move_to(p)

            half_size = sub_cube_size / 2.0
            cube_index = 0
            
          
            new_text_mobjects = []

            for i in range(3): # Z
                for j in range(3): # Y
                    for k in range(3): # X
                        center = self.sub_cube_centers[cube_index]
                        
                        min_bound = center - half_size
                        max_bound = center + half_size
                        
                        mask = (self.positions[:, 0] >= min_bound[0]) & (self.positions[:, 0] < max_bound[0]) & \
                               (self.positions[:, 1] >= min_bound[1]) & (self.positions[:, 1] < max_bound[1]) & \
                               (self.positions[:, 2] >= min_bound[2]) & (self.positions[:, 2] < max_bound[2])
                        
                        particles_in_this_cube = self.positions[mask]
                        entropy = calculate_entropy(particles_in_this_cube, center)

                        norm_entropy = np.clip(entropy / self.max_entropy_per_cube, 0, 1)
                        new_color = interpolate_color(RED, BLUE, norm_entropy)
                        
                        current_cube = self.rubiks_cube[cube_index]
                        current_cube.set_style(
                            fill_color=new_color,
                            stroke_color=new_color,
                            fill_opacity=0.4,
                            stroke_width=1.0
                        )
                        
                        
                        text_line = MarkupText(
                            f"Cube {cube_index+1}: {entropy:.2f}", 
                            font_size=self.font_size
                        )
                        text_line.set_color(new_color)
                        new_text_mobjects.append(text_line)

                        cube_index += 1
            
            self.remove_fixed_in_frame_mobjects(self.current_entropy_display)
            
           
            col1 = VGroup(*new_text_mobjects[0:9]).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
            col2 = VGroup(*new_text_mobjects[9:18]).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
            col3 = VGroup(*new_text_mobjects[18:27]).arrange(DOWN, buff=0.05, aligned_edge=LEFT)
            
            new_display_group = VGroup(col1, col2, col3).arrange(RIGHT, buff=0.2, aligned_edge=UP)
            new_display_group.to_corner(UL, buff=0.1)
            
           
            self.add_fixed_in_frame_mobjects(new_display_group)
            self.current_entropy_display = new_display_group\

            
        def update_scene_wrapper(dt):
            update_scene(None, dt) 

        self.add_updater(update_scene_wrapper)
        self.wait(5) 
        self.stop_ambient_camera_rotation()
        self.remove_updater(update_scene_wrapper)