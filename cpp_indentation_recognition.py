import copy
import numpy as np
from sklearn.cluster import MeanShift
from scipy import stats

class MeanShiftIndentationRecognizer:
    """
    Recognizes code indentation using Mean Shift clustering on x-coordinates.
    Language-agnostic: works for Python, C++, Java, etc.
    """
    
    def __init__(self, bandwidth=None):
        self.bandwidth = bandwidth
        self.INDENTATION = '    '  
        
    def recognize_indents(self, ocr_output, image_width):
        """
        Apply Mean Shift clustering to determine indentation levels.
        
        Args:
            ocr_output (list): Array of line dicts with 'text' and 'x' keys
            image_width (int): Width of the image
            
        Returns:
            dict: Result with 'code', 'lines' (with cluster labels), 'metadata'
        """
        if not ocr_output:
            return {
                'code': '',
                'lines': [],
                'metadata': {
                    'algorithm': 'meanshift',
                    'bandwidth': self.bandwidth,
                    'num_clusters': 0
                }
            }
        
        lines = copy.deepcopy(ocr_output)
        
        
        x_values = np.array([line['x'] for line in lines]).reshape(-1, 1)
        
        # Use provided bandwidth or estimate
        if self.bandwidth is None:
            bandwidth = self._estimate_bandwidth(x_values)
        else:
            bandwidth = self.bandwidth
        
        # Apply Mean Shift clustering
        mean_shift = MeanShift(bandwidth=bandwidth)
        mean_shift.fit(x_values)
        labels = mean_shift.labels_
        
        # Assign cluster labels to lines
        for i, line in enumerate(lines):
            line['cluster_label'] = int(labels[i])
        
        
        label_coords = {}
        for i, line in enumerate(lines):
            cluster = line['cluster_label']
            if cluster not in label_coords:
                label_coords[cluster] = []
            label_coords[cluster].append(line['x'])
        
        
        label_avgs = {cluster: np.mean(coords) for cluster, coords in label_coords.items()}
        
        
        sorted_labels = sorted(label_avgs.keys(), key=lambda k: label_avgs[k])
        label_to_indent = {label: indent_level for indent_level, label in enumerate(sorted_labels)}
        
        
        for line in lines:
            line['indentation_level'] = label_to_indent[line['cluster_label']]
        
      
        final_code = self._generate_code(lines)
        
        return {
            'code': final_code,
            'lines': lines,
            'metadata': {
                'algorithm': 'meanshift',
                'bandwidth': float(bandwidth),
                'num_clusters': len(sorted_labels),
                'cluster_to_indent_mapping': label_to_indent
            }
        }
    
    def _estimate_bandwidth(self, x_values):
        """Estimate bandwidth based on data distribution."""
        
        diffs = np.diff(np.sort(x_values.flatten()))
        mean_diff = np.mean(diffs[diffs > 0]) if len(diffs[diffs > 0]) > 0 else 30
        return mean_diff * 1.5
    
    def _generate_code(self, lines):
        """Generate formatted code with proper indentation."""
        code = ''
        for line in lines:
            indent_level = line['indentation_level']
            indent = self.INDENTATION * indent_level
            text = line['text'].strip()
            code += indent + text + '\n'
        return code


def apply_mean_shift_indentation(ocr_output, image_width, bandwidth=None):
    """
    Convenience function to apply Mean Shift indentation recognition.
    
    Args:
        ocr_output (list): Array of OCR line dicts
        image_width (int): Image width
        bandwidth (float, optional): Bandwidth for Mean Shift
        
    Returns:
        dict: Result with corrected code and metadata
    """
    recognizer = MeanShiftIndentationRecognizer(bandwidth=bandwidth)
    return recognizer.recognize_indents(ocr_output, image_width)