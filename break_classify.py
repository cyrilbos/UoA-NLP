import random

from nltk.tokenize import sent_tokenize

from Database.DatabaseHelper import DatabaseHelper
from Database.Configuration import connection_string

from ML.Classifier import Classifier
from ML.KMeansClusterizer import KMeansClusterizer
from ML.Recommender import Recommender


dbmg = DatabaseHelper(connection_string)
questions = dbmg.get_questions_content()
data, target, target_names = dbmg.get_training_data('Business')

###################################

forum_question_classifier = Classifier(data, target, target_names)

print('Precision of the classifier on its training data set: ', forum_question_classifier.evaluate_precision())

### predict the category of every question, appending it into the corresponding list of the dictionary ###

predicted_categories = {}
cluster_data = {}
cluster_target = {}
for category_name in target_names:
    predicted_categories[category_name] = []
    cluster_data[category_name] = []
    cluster_target[category_name] = []


for question in questions:
    question = question.replace('?"', '? "').replace('!"', '! "').replace('."', '. "')
    for sentence in sent_tokenize(question):
        predicted_category_i = forum_question_classifier.predict([sentence])[0]
        predicted_categories[forum_question_classifier.target_names[predicted_category_i]].append(sentence)

for category in predicted_categories:
    print('####Category: ' + category)
    nb = 10 if len(predicted_categories[category]) >= 10 else len(predicted_categories[category])
    for i in range(nb):
        print(predicted_categories[category][i])

##########################################################################################################


### Compute and print clusters ###
cluster_target_names = []
category_i = 0

question_recommender = Recommender()

for category in predicted_categories:
    if len(predicted_categories[category]) > 0:
        #cluster_target_names.append(category)
        for sentence in predicted_categories[category]:
            cluster_data[category].append(sentence)
            cluster_target[category].append(category_i)
        #Split the set of documents into clusters of ~3 documents
        n_clusters = int(len(cluster_data[category]) / 3)

        clusterizer = KMeansClusterizer(cluster_data[category], cluster_target[category], [category], n_features=10)

        km, X = clusterizer.idf_clusterize(n_clusters=n_clusters)

        #print the clusters and save them to a file
        clusters = [[] for dummy in range(n_clusters)]
        i = 0
        for cluster_num in km.labels_:
            clusters[cluster_num].append(cluster_data[category][i])
            i += 1

        n = 0

        save_file = open('broken_idf_clusters_{}_{}.txt'.format(category, n_clusters), 'w')

        for cluster in clusters:
            if len(cluster) > 1:
                #print('CLUSTER {}'.format(n))
                save_file.write('CLUSTER {}\n'.format(n))
                for doc in cluster:
                    #print(doc)
                    save_file.write(doc + '\n')
            n += 1

        """#Too heavy to run
        #"Clustering" the documents using a recommender
        recommend_data = {'id':[], 'description':[]}

        for i in range(len(cluster_data[category])):
            recommend_data['id'].append(i)
            recommend_data['description'].append(cluster_data[category][i])

        question_recommender.train(recommend_data)

        save_file = open('broken_idf_recommendations_{}.txt'.format(category), 'w')
        rnd = random.randint(0, 20)
        for item_to_recommend_index in range(rnd, rnd + rnd):
            print("Current item: ", recommend_data['description'][item_to_recommend_index])
            save_file.write("Current item: " + recommend_data['description'][item_to_recommend_index])
            recommended_items = question_recommender.predict(recommend_data['id'][item_to_recommend_index], 5)
            print("Recommended items: ")
            for recommended_item in recommended_items:
                print(recommend_data['description'][recommend_data['id'].index(int(recommended_item[1]))])
                save_file.write(recommend_data['description'][recommend_data['id'].index(int(recommended_item[1]))])

        category_i += 1
        """

#clusterizer.print_metrics(km, X)