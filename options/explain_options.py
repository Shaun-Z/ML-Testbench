from .base_options import BaseOptions


class ExplainOptions(BaseOptions):
    """This class includes explain options.

    It also includes shared options defined in BaseOptions.
    """

    def initialize(self, parser):
        parser = BaseOptions.initialize(self, parser)  # define shared options
        # default values
        parser.add_argument('--n_evals', type=int, default=5000, help='the number of iterations. The larger the number, the finer the granularity of the significance analysis and the longer the computation consumes time')
        parser.add_argument('--index_explain', type=list, default=[1], help='the index of the class to explain')
        parser.add_argument('--explanation_name', type=str, default='shap', help='the name of the explanation method')

        parser.add_argument('--results_dir', type=str, default='./results/', help='saves results here.')
        parser.add_argument('--aspect_ratio', type=float, default=1.0, help='aspect ratio of result images')
        parser.add_argument('--phase', type=str, default='val', help='train, val, test, etc')
        # Dropout and Batchnorm has different behavioir during training and test.
        parser.add_argument('--eval', action='store_true', help='use eval mode during explanation.')
        parser.add_argument('--num_test', type=int, default=50, help='how many test images to run')
        # rewrite devalue values
        parser.set_defaults(model='res_class')
        self.isTrain = False
        return parser