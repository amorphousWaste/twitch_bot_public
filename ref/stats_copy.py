"""Generate project stats."""

import os
import pygount
import rich

from radon.complexity import cc_rank
from radon.metrics import mi_visit, mi_rank
from radon.visitors import ComplexityVisitor
from rich.progress import Progress


class ObjectStat(object):
    """Object stats class."""

    def __init__(self) -> None:
        """Init."""
        super(ObjectStat, self).__init__()

        self._complexity_score = None
        self._complexity_rank = None

    @property
    def complexity_score(self) -> float:
        return self._complexity_score

    @complexity_score.setter
    def complexity_score(self, complexity_score: int) -> None:
        self._complexity_score = float('{:.2f}'.format(complexity_score))
        self.complexity_rank = self._complexity_score

    @property
    def complexity_rank(self) -> str:
        return self._complexity_rank

    @complexity_rank.setter
    def complexity_rank(self, complexity_score: float) -> str:
        self._complexity_rank = cc_rank(complexity_score)

    def __str__(self) -> str:
        return (
            f'complexity_score: {self._complexity_score} '
            f'(complexity_rank: {self._complexity_rank}'
        )


class ClassStat(ObjectStat):
    """Class stats class."""

    def __init__(self, cv_class: object) -> None:
        """Init."""
        super(ClassStat, self).__init__()

        self.complexity_score = cv_class.real_complexity


class MethodStat(ObjectStat):
    """Method stats class."""

    def __init__(self, cv_method: object) -> None:
        """Init."""
        super(MethodStat, self).__init__()

        self.complexity_score = cv_method.complexity


class FunctionStat(ObjectStat):
    """Function stats class."""

    def __init__(self, cv_function: object) -> None:
        """Init."""
        super(FunctionStat, self).__init__()

        self.complexity_score = cv_function.complexity


class FileStat(object):
    """File stats class."""

    def __init__(self) -> None:
        """Init."""
        super(FileStat, self).__init__()

        self._path = None

        self._source_analysis = None

        self._maintainability_score = None
        self._maintainability_rank = None

        self._classes = []
        self._functions = []

        self.total_complexity = 0

    @property
    def classes(self) -> list[object]:
        return self._classes

    @classes.setter
    def classes(self, classes: list[object]) -> None:
        for cv_class in classes:
            self.total_complexity += cv_class.real_complexity
            self._classes.append(ClassStat(cv_class))

            for method in cv_class.methods:
                self.total_complexity += method.complexity

    @property
    def functions(self) -> list[object]:
        return self._functions

    @functions.setter
    def functions(self, functions: list[object]) -> None:
        for function in functions:
            self._functions.append(function)
            self.total_complexity += function.complexity

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> None:
        self._path = path

    @property
    def source_analysis(self) -> str:
        return self._source_analysis

    @source_analysis.setter
    def source_analysis(
        self, source_analysis: pygount.analysis.SourceAnalysis
    ) -> str:
        self._source_analysis = source_analysis

    @property
    def maintainability_score(self) -> float:
        return self._maintainability_score

    @maintainability_score.setter
    def maintainability_score(self, maintainability_score: int) -> None:
        self._maintainability_score = float(
            '{:.2f}'.format(maintainability_score)
        )
        self.maintainability_rank = self._maintainability_score

    @property
    def maintainability_rank(self) -> str:
        return self._maintainability_rank

    @maintainability_rank.setter
    def maintainability_rank(self, maintainability_score: float) -> str:
        self._maintainability_rank = mi_rank(maintainability_score)

    def __str__(self) -> str:
        return (
            f'path: {self.path} '
            f'source_analysis: {self.source_analysis} '
            f'maintainability_score: {self.maintainability_score} '
            f'maintainability_rank: {self.maintainability_rank} '
            f'classes: {self.classes} '
            f'functions: {self.functions} '
            f'total_complexity: {self.total_complexity}'
        )


class BotStats(object):
    """Bot stats class."""

    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_FILE = os.path.join(PROJECT_DIR, 'bot_stats', 'stats.md')
    # File extensions to check.
    EXTS = 'json,md,py,sql,yaml'
    # Ignore auto-generated api files.
    FILES_TO_SKIP = 'obs_events.py,obs_requests.py'
    # Ignore folders containing irrelevant code.
    FOLDERS_TO_SKIP = 'docs,images,ref'

    def __init__(self) -> None:
        """Init."""
        super(BotStats, self).__init__()

        self.analyses = []
        self.project_summary = pygount.ProjectSummary()
        self.total_complexity = 0
        self.total_scanned = 0
        self.total_files = 0
        self.total_maintainability = 0

    def generate_pygount_analysis(self) -> None:
        """Complexity report in python."""
        # Build the pygount source scanner.
        source_scanner = pygount.analysis.SourceScanner(
            [self.PROJECT_DIR],
            suffixes=pygount.common.regexes_from(
                self.EXTS,
                default_patterns_text='*',
                source=None,
            ),
            folders_to_skip=pygount.common.regexes_from(
                self.FOLDERS_TO_SKIP,
                default_patterns_text=(
                    pygount.analysis.DEFAULT_FOLDER_PATTERNS_TO_SKIP_TEXT
                ),
                source=None,
            ),
            name_to_skip=pygount.common.regexes_from(
                self.FILES_TO_SKIP,
                default_patterns_text=(
                    pygount.analysis.DEFAULT_NAME_PATTERNS_TO_SKIP_TEXT
                ),
                source=None,
            ),
        )

        # Generate the default regexes.
        generated_regexes = pygount.common.regexes_from(
            pygount.analysis.DEFAULT_GENERATED_PATTERNS_TEXT
        )

        # Scan each file path with pygount.
        with Progress(transient=True) as progress:
            try:
                for source_path, group in progress.track(
                    list(source_scanner.source_paths()),
                    description='Scanning with pygount...',
                ):
                    file_stat = FileStat()
                    file_stat.path = source_path
                    file_stat.source_analysis = (
                        pygount.analysis.SourceAnalysis.from_file(
                            source_path,
                            group,
                            'automatic',
                            'utf-8',
                            generated_regexes=generated_regexes,
                            duplicate_pool=pygount.analysis.DuplicatePool(),
                        )
                    )

                    self.analyses.append(file_stat)
                    self.project_summary.add(file_stat.source_analysis)

            except Exception as e:
                rich.print(f'Unable to scan {source_path}: {e}')

            finally:
                progress.stop()

    def create_pygount_summary_table(self) -> str:
        """Convert the pygount project summary to a markdown table.

        Returns:
            md (str): Pygount summary table in markdown.
        """
        md = []

        # Get and sort the project summaries by most used language.
        language_summaries = sorted(
            self.project_summary.language_to_language_summary_map.values(),
            key=lambda l: l.code_count,
            reverse=True,
        )

        # Create the table header.
        md.append(
            '|Language|File Count|Code Count|Documentation Count|Empty Count|'
            'String Count|'
        )
        md.append('|---|---|---|---|---|---|')

        # Add each language summary to the table.
        for ls in language_summaries:
            language = ls.language.strip('__')
            md.append(
                f'|{language}|{ls.file_count}|{ls.code_count}|'
                f'{ls.documentation_count}|{ls.empty_count}|{ls.string_count}|'
            )

        return '\n'.join(md)

    def generate_radon_complexity_report(self) -> None:
        """Generate a complexity report from radon."""
        # Get only the python files from the pygount analysis.
        python_files = [
            a for a in self.analyses if a.source_analysis.language == 'Python'
        ]

        self.total_files = len(python_files)

        with Progress(transient=True) as progress:
            for analysis in progress.track(
                python_files, description='Calculating radon scores...'
            ):
                with open(analysis.path, 'r') as in_file:
                    data = in_file.read()

                    # Calculate the maintainability score for the file.
                    maintainability_score = mi_visit(data, False)
                    analysis.maintainability_score = maintainability_score
                    self.total_maintainability += maintainability_score

                    # Calculate the complexity score for the file.
                    visitor = ComplexityVisitor.from_code(data)
                    analysis.classes = visitor.classes
                    analysis.function = visitor.classes

            progress.stop()

    def create_radon_markdown(self) -> str:
        """Convert the radon data to markdown.

        Returns:
            str: radon data in markdown.
        """
        md = []

        with Progress(transient=True) as progress:
            for analysis in progress.track(
                self.analyses,
                description='Building markdown report...',
            ):
                md.append(f'`{analysis.path}`  ')
                md.append('### Maintainability ###')
                md.append(
                    '{} (*{}*)'.format(
                        float('{:.2f}'.format(analysis.maintainability_score)),
                        analysis.maintainability_rank,
                    )
                )

                if analysis.classes or analysis.functions:
                    md.append('### Complexity ###')

                for a_class in analysis.classes:
                    class_complexity = a_class.real_complexity
                    class_rank = cc_rank(class_complexity)
                    class_prefix = (
                        '└' if a_class == analysis.classes[-1] else '├'
                    )
                    md.append(
                        '&nbsp;&nbsp;&nbsp;&nbsp;'
                        f'{class_prefix} Class: `{a_class.name}`: '
                        f'{class_complexity} (*{class_rank}*)  '
                    )

                    for method in a_class.methods:
                        method_complexity = method.complexity
                        method_rank = cc_rank(method_complexity)
                        method_prefix = (
                            '└' if method == a_class.methods[-1] else '├'
                        )
                        md.append(
                            '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                            f'{method_prefix} Method: `{method.name}`: '
                            f'{method_complexity} (*{method_rank}*)  '
                        )

                        self.total_scanned += 1

                    self.total_complexity += analysis.total_complexity

                for a_function in analysis.functions:
                    function_complexity = a_function.complexity
                    function_rank = cc_rank(function_complexity)
                    function_prefix = (
                        '└' if a_function == analysis.functions[-1] else '├'
                    )
                    md.append(
                        '&nbsp;&nbsp;&nbsp;&nbsp;'
                        f'{function_prefix} Function: `{a_function.name}`: '
                        f'{function_complexity} (*{function_rank}*)  '
                    )
                    self.total_complexity += function_complexity
                    self.total_scanned += 1

                md.append('\n---\n')

        average_maintainability = '{:.2f}'.format(
            self.total_maintainability / self.total_files
        )
        average_maintainability_rank = mi_rank(float(average_maintainability))

        md.insert(
            0,
            f'**Average Maintainability**: {average_maintainability} '
            f'(*{average_maintainability_rank}*)\n',
        )

        average_complexity = '{:.2f}'.format(
            self.total_complexity / self.total_scanned
        )
        average_complexity_rank = cc_rank(float(average_complexity))

        md.insert(
            0,
            f'**Average Complexity**: {average_complexity} '
            f'(*{average_complexity_rank}*)\n',
        )

        return '\n'.join(md)

    def create_radon_maintainability_markdown(self) -> str:
        """Convert the radon maintainability data to markdown.

        Returns:
            str: radon data in markdown.
        """
        md = []
        for path in self.maintainability:
            score = self.maintainability[path]['score']
            rank = self.maintainability[path]['rank']
            md.append(f'`{path}`: {score} (*{rank}*)  ')

        return '\n'.join(md)

    def generate_stats_report(self) -> None:
        """Generate the project stats report."""
        # Generate the reports.
        self.generate_pygount_analysis()
        pygount_table = self.create_pygount_summary_table()
        self.generate_radon_complexity_report()
        radon_report = self.create_radon_markdown()

        # Compile the md file.
        md_file = [
            '# Project Statistics #',
            'Generated by `stats.py`',
            '## Project Code Summary ##',
            pygount_table,
            '\n\n---\n',
            '## Project Complexity Report ##',
            radon_report,
        ]

        with open(self.OUTPUT_FILE, 'w') as out_file:
            out_file.write('\n'.join(md_file))

        rich.print('Done')


if __name__ == '__main__':
    bot_stats = BotStats()
    bot_stats.generate_stats_report()
