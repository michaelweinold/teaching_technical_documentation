import pandas as pd


def create_sample_dataframe() -> pd.DataFrame:
    """
    Creates a sample DataFrame with the following columns:

    - uid: unique identifier for each row.
    - production: production amount.
    - production_user: user-supplied production amount.
    - branch: list of uids of upstream nodes.

    .. image:: https://upload.wikimedia.org/wikipedia/commons/d/d6/Shift_graph_line_representation.png

    Notes
    -----

    This function is used only to illustrate the use of 
    the `Sphinx documentation generator <https://en.wikipedia.org/wiki/Sphinx_(documentation_generator)>`_
    in documenting Python code. As you can see, we can add images, hyperlinks and scientific-style references [1]_.

    References
    ----------
    .. [1] Mutel, C. 2017. Brightway: An open source framework for Life Cycle Assessment. Journal of Open Source Software, 12:2. https://doi.org/10.21105%2Fjoss.00236.
    
    Returns
    -------
    pd.DataFrame
        Sample DataFrame.
    """

    data = {
        'uid': [0, 1, 2, 3, 4, 5, 6],
        'production': [1, 0.5, 0.2, 0.1, 0.1, 0.05, 0.01],
        'production_user': [None, 0.25, None, None, 0.18, None, None],
        'branch': [[], [0], [0, 1], [0], [0, 1, 2], [0, 1, 2, 4], [0, 1, 2, 4, 5]]
    }

    return pd.DataFrame(data)


def update_production_based_on_user_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Updates the production amount of all nodes which are upstream
    of a node with user-supplied production amount.
    If an upstream node has half the use-supplied production amount,
    then the production amount of all downstream node is also halved.

    For instance, given a DataFrame of the kind:

    +-----+------------+-----------------+------------------+
    | uid | production | production_user | branch           |
    +=====+============+=================+==================+
    | 0   | 1          | NaN             | []               |
    +-----+------------+-----------------+------------------+
    | 1   | 0.5        | 0.25            | [0,1]            |
    +-----+------------+-----------------+------------------+
    | 2   | 0.2        | NaN             | [0,1,2]          |
    +-----+------------+-----------------+------------------+
    | 3   | 0.1        | NaN             | [0,3]            |
    +-----+------------+-----------------+------------------+
    | 4   | 0.1        | 0.18            | [0,1,2,4]        |
    +-----+------------+-----------------+------------------+
    | 5   | 0.05       | NaN             | [0,1,2,4,5]      |
    +-----+------------+-----------------+------------------+
    | 6   | 0.01       | NaN             | [0,1,2,4,5,6]    |
    +-----+------------+-----------------+------------------+

    The function returns a DataFrame of the kind:

    +-----+-------------------+------------------+
    | uid | production        | branch           |
    +=====+===================+==================+
    | 0   | 1                 | []               |
    +-----+-------------------+------------------+
    | 1   | 0.25              | [0,1]            |
    +-----+-------------------+------------------+
    | 2   | 0.2 * (0.25/0.5)  | [0,1,2]          |
    +-----+-------------------+------------------+
    | 3   | 0.1               | [0,3]            |
    +-----+-------------------+------------------+
    | 4   | 0.18              | [0,1,2,4]        |
    +-----+-------------------+------------------+
    | 5   | 0.05 * (0.1/0.18) | [0,1,2,4,5]      |
    +-----+-------------------+------------------+
    | 6   | 0.01 * (0.1/0.18) | [0,1,2,4,5,6]    |
    +-----+-------------------+------------------+


    As we can see, the function updates production only
    for those nodes upstream of a node with 'production_user':

    - Node 2 is upstream of node 1, which has a 'production_user' value.
    - Node 3 is NOT upstream of node 1. It is upstream of node 0, but node 0 does not have a 'production_user' value.

    As we can see, the function always takes the "most recent"
    'production_user' value upstream of a node:

    - Node 5 is upstream of node 4, which has a 'production_user' value.
    - Node 4 is upstream of node 1, which also has a 'production_user' value.

    In this case, the function takes the 'production_user' value of node 4, not of node 1.

    See Also
    --------
    create_sample_dataframe: Create a sample DataFrame for use in this function.

    Examples
    --------
    >>> mypackage.update_production_based_on_user_data(df = my_dataframe)
    +-----+-------------------+------------------+
    | uid | production        | branch           |
    +=====+===================+==================+
    | 0   | 1                 | []               |
    +-----+-------------------+------------------+
    | 1   | 0.25              | [0,1]            |
    +-----+-------------------+------------------+

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame. Must have the columns 'production', 'production_user' and 'branch'.

    Returns
    -------
    pd.DataFrame
        Output DataFrame.
    """

    df_user_input_only = df[df['production_user'].notna()]
    dict_user_input = dict(zip(df_user_input_only['uid'], df_user_input_only['production_user']))

    def multiplier(row):
        for branch_uid in reversed(row['branch']):
            if branch_uid in dict_user_input:
                return row['production'] * dict_user_input[branch_uid]
        return row['production']

    df['production'] = df.apply(multiplier, axis=1)

    return df