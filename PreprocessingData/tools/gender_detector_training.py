import pandas as pd
from pathlib import Path
import text_cleaner

def test():

    cols = ["gender","raw_text", 'title']
    file_path = input("Enter .csv file with correctly labelled gender and text: ")
    # default is "./(V1.8)all_products_data_set.csv"
    p = Path(file_path)
    
    while not p.exists():
        
        file_path = input("invalid file path re-enter or 'quit()' for quit program: ")
        if file_path == 'quit()' or file_path == '' :
            return 
        p = Path(file_path)
    
    df = pd.read_csv(file_path, usecols=cols)
    for row in range(df.shape[0]):
        df.loc[row, 'raw_text'] = text_cleaner.raw_content(df.loc[row, 'title'], None, df.loc[row, 'raw_text'], None)
    # drop the title column since the title already combined to the raw text
    df = df[['gender','raw_text']].copy()

    df = df[pd.notnull(df['raw_text'])]
    df = df[pd.notnull(df['gender'])]
    
    #modify names of columns
    df.rename(columns={"gender":"Gender", 'raw_text':"Product_Description"}, inplace=True)
    #drop the unknown/unset/broken
    index_broken = df[((df.Gender == "broken") | (df.Gender == "unknown") | (df.Gender == "unset") |(df.Gender == 'unisex/unknown'))].index
    df = df.drop(index_broken)
    #create dict of gender and num 
    df['gender_id'] = df['Gender'].factorize()[0]
    
    category_id_df = df[['Gender', 'gender_id']].drop_duplicates().sort_values('gender_id')
    category_to_id = dict(category_id_df.values)
    id_to_category = dict(category_id_df[['gender_id', 'Gender']].values)
    ###########modify the bias
    temp_df = df.query('(Gender == "men")').sample(n=4000)
    index_men = df[(df.Gender == "men")].index
    df = df.drop(index_men)

    df = pd.concat([df, temp_df])

    temp_df = df.query('(Gender == "women")').sample(n=4000)
    index_women = df[(df.Gender == "women")].index

    df = df.drop(index_women)
    df = pd.concat([df, temp_df])
    df = df.sort_index()
    #############
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
    features = tfidf.fit_transform(df.Product_Description).toarray()
    labels = df.gender_id
    from sklearn.feature_selection import chi2
    import numpy as np

    # N = 2
    # for Gender, gender_id in sorted(category_to_id.items()):
    #     features_chi2 = chi2(features, labels == gender_id)
    #     indices = np.argsort(features_chi2[0])
    #     feature_names = np.array(tfidf.get_feature_names())[indices]
    #     unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
    #     bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
    #     print("# '{}':".format(Gender))
    #     print("  . Most correlated unigrams:\n       . {}".format('\n       . '.join(unigrams[-N:])))
    #     print("  . Most correlated bigrams:\n       . {}".format('\n       . '.join(bigrams[-N:])))
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from sklearn.naive_bayes import MultinomialNB
    X_train, X_test, y_train, y_test = train_test_split(df['Product_Description'], df['Gender'], random_state = 0)
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(X_train)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    clf = MultinomialNB().fit(X_train_tfidf, y_train)

    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import LinearSVC
    from sklearn.model_selection import cross_val_score

    models = [
        RandomForestClassifier(n_estimators=200, max_depth=3, random_state=0),
        LinearSVC(),
        MultinomialNB(),
        LogisticRegression(random_state=0),
    ]
    CV = 5
    cv_df = pd.DataFrame(index=range(CV * len(models)))
    entries = []
    
    for model in models:
        model_name = model.__class__.__name__
        accuracies = cross_val_score(model, features, labels, scoring='accuracy', cv=CV)
        for fold_idx, accuracy in enumerate(accuracies):
            entries.append((model_name, fold_idx, accuracy))
    cv_df = pd.DataFrame(entries, columns=['model_name', 'fold_idx', 'accuracy'])
    print(cv_df.groupby('model_name')['accuracy'].mean())
    df = df.reset_index()

    model = LinearSVC()
    X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(features, labels, df.index, test_size=0.33, random_state=0)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    model.fit(features, labels)
    N = 2
    # for Product, category_id in sorted(category_to_id.items()):
    #     indices = np.argsort(model.coef_[category_id])
    #     feature_names = np.array(tfidf.get_feature_names())[indices]
    #     unigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 1][:N]
    #     bigrams = [v for v in reversed(feature_names) if len(v.split(' ')) == 2][:N]

    from sklearn import metrics
    print(metrics.classification_report(y_test, y_pred, target_names=df['Gender'].unique()))
    ##################################Save Models##############################################

    import pickle
    import os
    #save statistics model
    filename = '/text_classifier/gender_detector_model.pkl'
    os.mkdir(os.path.dirname(filename))
    with open(filename, 'wb') as f:
        pickle.dump(model,f)
    #save the vectorizer

    pickle.dump(tfidf, open("/text_classifier/vectorizer.pkl", "wb"))
if __name__ == '__main__':
    test()