from django.shortcuts import render ,get_object_or_404
from django.http import HttpResponse ,Http404, HttpResponseRedirect
from accounts.models import Ingredients
from accounts.models import recipes , Preferences
from accounts.models import Rating as  Rating1
from accounts.models import steps
from django.shortcuts import render,redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .forms import  AddRatingForm
from math import sqrt
#cosine
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def Recipe_information_with_rating(recipe_id):
    # This function returns the entire recipe data for use in Recipe_page function to  displaying it in the HTML page
    Allـrecipes = get_object_or_404(recipes, pk=recipe_id)
    All_steps = get_object_or_404(steps, pk=recipe_id)
    All_ingredients = get_object_or_404(Ingredients, pk=recipe_id)
    params = {'Allـrecipes': Allـrecipes ,'All_steps' :All_steps , 'All_ingredients':All_ingredients}
    return params

def Recipe_information( request ,recipe_id):
    # This function returns the entire recipe data for use in displaying it in the HTML page and most_popular recipe When the user is not logged in
    Allـrecipes = get_object_or_404(recipes, pk=recipe_id)
    All_steps = get_object_or_404(steps, pk=recipe_id)
    All_ingredients = get_object_or_404(Ingredients, pk=recipe_id)
    thesimmlr_recipe = thesimmlr(request ,recipe_id)
    popular = most_popular()
    popular = popular.to_dict('records')


    return render(request , 'recipe_page2.html',{'Allـrecipes': Allـrecipes ,'All_steps' :All_steps , 'All_ingredients':All_ingredients , 'thesimmlr_recipe':thesimmlr_recipe ,'popular':popular})


def Recipe_page(request , recipe_id ):
    # This function returns the entire recipe data for use in displaying it on the HTML page and able him to rate the recipe
    thesimmlr_recipe = thesimmlr(request ,recipe_id)
    if request.user.is_authenticated:
        params = Recipe_information_with_rating(recipe_id)
        params['user'] = request.user
        if request.method == 'POST':
            userid = request.POST.get('userid')
            u = User.objects.get(pk=userid)
            m = recipes.objects.get(pk=recipe_id )
            rfm = AddRatingForm(request.POST)
            params['rform'] = rfm
            params['thesimmlr_recipe']=thesimmlr_recipe
            if rfm.is_valid():
                rat = rfm.cleaned_data['rating']
                count = Rating1.objects.filter(user=u, recipe=m).count()
                if (count > 0):
                    messages.warning(request, 'لقد قيمت الوصفة سابقاً')
                    return render(request, 'recipe_page.html' ,params  )
                action = Rating1(user=u, recipe=m, rating=rat)
                action.save()
                messages.success(request, 'قمت بتقييم' + ' ' + rat + ' ' + "نجمة/نجمات !")
            return render(request, 'recipe_page.html',params  )
        else:
            rfm = AddRatingForm()
            params['rform'] = rfm
            params['thesimmlr_recipe']=thesimmlr_recipe

            return render(request, 'recipe_page.html', params )
    else:
        return HttpResponseRedirect('login')


def most_popular():
    # This function brings recipes that have received more reviews from users
     Rating = Rating1.objects.all()
     x = []
     y = []
     for item in Rating:
        x = [item.id, item.user, item.recipe_id,item.recipe]
        y += [x]
     Rating_df = pd.DataFrame(y, columns=['id', 'user', 'recipe_id','count'])
     count_Rating_df =pd.DataFrame(Rating_df.groupby('recipe_id')['count'].count())
     sort_Rating_df = count_Rating_df.merge(Rating_df, on=['recipe_id'], how='left')
     sort_Rating_df =sort_Rating_df.sort_values('count_x', ascending=False)

     x = []
     y = []
     for i in sort_Rating_df['recipe_id']:
         for item in recipes.objects.filter(id=i):
             x = [item.id, item.name, item.Ingredients, item.recipesduration, item.sections, item.image]
             y += [x]
     df_drop_duplicates = pd.DataFrame(y, columns=['id', 'name', 'Ingredients', 'recipesduration', 'sections', 'image'])
     # dropping ALL duplicate recipes
     df_drop_duplicates = df_drop_duplicates.drop_duplicates()
     return  df_drop_duplicates




def home(request):
    #this is the main function in this project and it is displaying  all elements in  home page

        #  searches by the name of the recipe and displaying the search results
        Search_Results = []
        if 'q' in request.GET:
            q = request.GET['q']
            Search_Results = recipes.objects.filter(name__icontains=q)
            if  Search_Results.count() == 0 :
                messages.warning(request, 'لاتوجد نتائج بحث مطابقة ')
        recipe = recipes.objects.all()
    # Ensure that the user is logged in to view recommendations
        if request.user.is_authenticated:
            # calling function content based and collaborative filtering
           recommended1 = Recommendation_CB(request)
           recommended2 = Recommendation_CF(request)

           if recommended1 :
               if recommended2:
                return render(request, 'home.html', {'recommended1':recommended1,'recommended2':recommended2,'recipe':recipe ,'Search_Results':Search_Results})
               else:
                   popular = most_popular()
                   popular = popular.to_dict('records')
                   return render(request, 'home.html', {'most_popular': popular,'recipe':recipe ,'range': range(1,10),'Search_Results':Search_Results})
           else:
               popular = most_popular()
               popular = popular.to_dict('records')
               return render(request, 'home.html', {'most_popular':popular ,'recipe':recipe ,'range': range(1,10),'Search_Results':Search_Results})



        else:
           popular = most_popular()
           popular = popular.to_dict('records')
           return render(request, 'home.html',{'recipe':recipe ,'most_popular':popular ,'range': range(1,10),'Search_Results':Search_Results})

def Recommendation_CF(request):
    #   This function makes a recommendation to use a collaborative filter using the Pearson equation
    if request.user.is_authenticated:
            recipe = recipes.objects.all()
            rating = Rating1.objects.all()
            x = []
            y = []
            A = []
            B = []
            C = []
            D = []
            # Movie Data Frames
            for item in recipe:
                x =  [ item.id ,item.name ,item.Ingredients, item.recipesduration, item.sections,item.description,item.image]
                y += [x]
            recipe_df = pd.DataFrame(y, columns=['recipeId', 'name', 'Ingredients', 'recipesduration', 'sections','description','image'])
            for item in rating:
                A = [item.user.id, item.recipe, item.rating,]
                B += [A]
            rating_df = pd.DataFrame(B, columns=['userId', 'recipeId', 'rating'])
            rating_df['userId'] = rating_df['userId'].astype(str).astype(np.int64)
            rating_df['recipeId'] =rating_df['recipeId'].astype(str).astype(np.int64)
            rating_df['rating'] = rating_df['rating'].astype(str).astype(np.float32)
            if request.user.is_authenticated:
                userid = request.user.id
                # select related is join statement in django.It looks for foreign key and join the table
                userInput = Rating1.objects.select_related('recipe').filter(user=userid)
                if userInput.count() == 0:
                    recommenderQuery = None
                    userInput = None
                else:
                    for item in userInput:
                        C = [item.recipe.name, item.rating]
                        D += [C]
                    inputrecipe = pd.DataFrame(D, columns=['name', 'rating'])
                    inputrecipe['rating'] = inputrecipe['rating'].astype(str).astype(np.float)
                    # Filtering out the recipe by title
                    inputId = recipe_df[recipe_df['name'].isin(inputrecipe['name'].tolist())]
                    # Then merging it so we can get the recipeId. It's implicitly merging it by title.
                    inputrecipe = pd.merge(inputId , inputrecipe)
                    # #Dropping information we won't use from the input dataframe
                    # Final input dataframe
                    # If a recipe you added in above isn't here, then it might not be in the original
                    # dataframe or it might spelled differently, please check capitalisation.
                    # Filtering out users that have raet recipe that the input has raeted and storing it
                    userSubset = rating_df[rating_df['recipeId'].isin(inputrecipe['recipeId'].tolist())]
                    # Groupby creates several sub dataframes where they all have the same value in the column specified as the parameter
                    userSubsetGroup = userSubset.groupby(['userId'])
                    # Sorting it so users with movie most in common with the input will have priority
                    userSubsetGroup = sorted(userSubsetGroup, key=lambda x: len(x[1]), reverse=True)
                    userSubsetGroup = userSubsetGroup[0:]
                    # Store the Pearson Correlation in a dictionary, where the key is the user Id and the value is the coefficient
                    pearsonCorrelationDict = {}
                    # For every user group in our subset
                    for name, group in userSubsetGroup:
                        # Let's start by sorting the input and current user group so the values aren't mixed up later on
                        group = group.sort_values(by='recipeId')
                        inputrecipe = inputrecipe.sort_values(by='recipeId')
                        # Get the N for the formula
                        nRatings = len(group)
                        # Get the review scores for the recipe that they both have in common
                        temp_df = inputrecipe[inputrecipe['recipeId'].isin(group['recipeId'].tolist())]
                        # And then store them in a temporary buffer variable in a list format to facilitate future calculations
                        tempRatingList = temp_df['rating'].tolist()
                        # Let's also put the current user group reviews in a list format
                        tempGroupList = group['rating'].tolist()
                        # Now let's calculate the pearson correlation between two users, so called, x and y
                        Sxx = sum([i ** 2 for i in tempRatingList]) - pow(sum(tempRatingList), 2) / float(nRatings)
                        Syy = sum([i ** 2 for i in tempGroupList]) - pow(sum(tempGroupList), 2) / float(nRatings)
                        Sxy = sum(i * j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList) * sum(
                            tempGroupList) / float(nRatings)
                        # If the denominator is different than zero, then divide, else, 0 correlation.
                        if Sxx != 0 and Syy != 0:
                            pearsonCorrelationDict[name] = Sxy / sqrt(Sxx * Syy)
                        else:
                            pearsonCorrelationDict[name] = 0
                    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
                    pearsonDF.columns = ['similarityIndex']
                    pearsonDF['userId'] = pearsonDF.index
                    pearsonDF.index = range(len(pearsonDF))
                    topUsers = pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:]
                    topUsersRating = topUsers.merge(rating_df, left_on='userId', right_on='userId', how='inner')
                    topUsersRating.head()
                    # Multiplies the similarity by the user's ratings
                    topUsersRating['weightedRating'] = topUsersRating['similarityIndex'] * topUsersRating['rating']
                    topUsersRating.head()
                    # Applies a sum to the topUsers after grouping it up by userId
                    tempTopUsersRating = topUsersRating.groupby('recipeId').sum()[['similarityIndex', 'weightedRating']]
                    tempTopUsersRating.columns = ['sum_similarityIndex', 'sum_weightedRating']
                    tempTopUsersRating.head()
                    # Creates an empty dataframe
                    recommendation_df = pd.DataFrame()
                    # Now we take the weighted average
                    recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
                    recommendation_df['recipeId'] = tempTopUsersRating.index
                    recommendation_df.head()
                    recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending= False)
                    recommender = recipe_df.loc[recipe_df['recipeId'].isin(recommendation_df.head(11)['recipeId'].tolist())]
                    recommender.index = range(len(recommender))
                    # here we filter recipes based on user preferences in terms of allergies to substances such as milk, wheat and eggs
                    userid = request.user.id
                    preferences = Preferences.objects.filter(user= userid)
                    x = []
                    y = []
                    for item in preferences:
                        x = [item.id, item.type, item.allergy]
                        y += [x]
                    preferences_df = pd.DataFrame(y, columns=['id','type','allergy'])
                    for index,row in recommender.iterrows():
                        if str(preferences_df.iat[0,2])=='قمح':
                                all = ['قمح','دقيق','طحين','خبز']
                                for i in all :
                                    check= " "+ i +" "
                                    if check in (" " + row['Ingredients'] + " "):
                                        recipeId = row['recipeId']
                                        recommender = recommender.set_index('recipeId')
                                        recommender= recommender.drop(index=recipeId)
                                        recommender['recipeId'] = recommender.index
                                        recommender.index = range(len(recommender))
                                        continue
                        if str(preferences_df.iat[0,2])=='بيض':
                            all = ['بيضتان','بيضتين','بيضات','بيض']
                            for i in all :
                                check= " "+ i +" "
                                if check in (" " + row['Ingredients'] + " "):
                                    recipeId = row['recipeId']
                                    recommender = recommender.set_index('recipeId')
                                    recommender= recommender.drop(index=recipeId)
                                    recommender['recipeId'] = recommender.index
                                    recommender.index = range(len(recommender))
                                    continue
                        if str(preferences_df.iat[0, 2]) == 'حليب':
                            all =['حليب']
                            for i in all:
                                check = " " + i + " "

                                if check in (" " + row['Ingredients'] + " "):
                                    recipeId = row['recipeId']
                                    recommender = recommender.set_index('recipeId')
                                    recommender= recommender.drop(index=recipeId)
                                    recommender['recipeId'] = recommender.index
                                    recommender.index = range(len(recommender))
                                    continue
                    recommender.index = range(len(recommender))
                    recipe_recommender = []
                    for i in recommender['recipeId']:
                         recipe_recommender += (recipes.objects.filter(pk=i))
                    r = []
                    o = []
                    for item in recipe_recommender:
                        r = [item.pk,item.name, item.image, item.sections, item.description, item.Ingredients_id, item.Ingredients, item.recipesduration]
                        o += [r]
                    recommender_df = pd.DataFrame(o,columns=['recipeId','name', 'image', 'sections', 'description', 'Ingredients_id', 'Ingredients', 'recipesduration'])
                    return recommender_df.to_dict('records')


def thesimmlr(request ,recipe_id ):
        recipe = recipes.objects.all()
        x = []
        y = []
        for item in recipe:
            x = [item.id, item.name, item.Ingredients, item.description, item.sections]
            y += [x]
        df = pd.DataFrame(y, columns=['id', 'name', 'Ingredients', 'description', 'sections'])
        features = ['Ingredients']
        for feature in features:
            df[feature] = df[feature].fillna('')
        df["combined_features"] = df.apply(combined_features, axis=1)
        # Convert words to vector to calculate similarity
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(df["combined_features"])
        print("Count Matrix:", count_matrix.toarray())
        cosine_sim = cosine_similarity(count_matrix)
        print(cosine_sim)
        # Find recipes that are similar to the recipes rated by the user
        sorted_similar_recipe_2 = []
        recipe_index = recipe_id
        similar_recipe = list(enumerate(cosine_sim[recipe_index]))
        sorted_similar_recipe = sorted(similar_recipe, key=lambda x: x[1], reverse=True)
        sorted_similar_recipe_2 += sorted_similar_recipe_titel(sorted_similar_recipe,request)
        print("*****************************")
        print(sorted_similar_recipe_2)
        return sorted_similar_recipe_2


def Recommendation_CB(request):
    # This function makes a recommendation to use a content-based filter using cosine similarity
    if request.user.is_authenticated:
        recipe = recipes.objects.all()
        x = []
        y = []
        for item in recipe:
            x = [ item.id ,item.name ,item.Ingredients, item.description, item.sections]
            y += [x]
        df = pd.DataFrame(y,columns=['id','name','Ingredients', 'description', 'sections'])
        features = ['Ingredients']
        for feature in features:
            df[feature] = df[feature].fillna('')
        df["combined_features"] = df.apply(combined_features, axis=1)
        # Convert words to vector to calculate similarity
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(df["combined_features"])
        print("Count Matrix:", count_matrix.toarray())
        cosine_sim = cosine_similarity(count_matrix)
        print(cosine_sim)
        user_reting = Rating1.objects.filter(user=request.user.id)
        #Find recipes that are similar to the recipes rated by the user
        sorted_similar_recipe_2 =[]
        for item in user_reting:
            recipe_index = item.recipe.id
            similar_recipe = list(enumerate(cosine_sim[recipe_index]))
            sorted_similar_recipe = sorted(similar_recipe, key=lambda x: x[1], reverse=True)
            sorted_similar_recipe_2 += sorted_similar_recipe_titel(sorted_similar_recipe,request)
        print("*****************************")
        print(sorted_similar_recipe_2)
        return sorted_similar_recipe_2
def combined_features(row):
    # This function collects the characteristics by which we will measure similarity
    #return  row['Ingredients'] + " " + row['description'] + " " + row['sections']
    return  row['Ingredients']

def get_title_from_index(id):
    recipe = recipes.objects.all()
    x = []
    y = []
    for item in recipe:
        x = [item.id, item.name, item.Ingredients, item.recipesduration, item.sections]
        y += [x]
    df = pd.DataFrame(y, columns=['id', 'name', 'Ingredients', 'recipesduration', 'sections'])
    return df[df.index == id]["name"].values[0]
def sorted_similar_recipe_titel(sorted_similar_recipe,request ):
    # This function ranks recipes based on the highest similarity value
    sorted_similar_recipe_titel = []
    sorted = []
    for recipe in sorted_similar_recipe:
        sorted_similar_recipe_titel.append((get_title_from_index(recipe[0])))
        if request.user.is_authenticated:
           sorted_similar_recipe_titel = Filterـrecipesـbasedـonـpreferences(sorted_similar_recipe_titel,request)
        sorted += dict.fromkeys(sorted_similar_recipe_titel, "In stock")

    return sorted
def Filterـrecipesـbasedـonـpreferences(sorted_similar_recipes ,request):
    #This function filters recipes based on user preferences in terms of allergies to substances such as milk, wheat and eggs
    re = []
    for item in sorted_similar_recipes:
        re += recipes.objects.filter(name=item)
    x = []
    y = []
    for item in re:
        x = [item.id, item.name, item.Ingredients, item.recipesduration, item.sections]
        y += [x]

    recommender = pd.DataFrame(y,
                               columns=['recipeId', 'name', 'Ingredients', 'recipesduration', 'sections'])
    userid = request.user.id
    preferences = Preferences.objects.filter(user=userid)
    x = []
    y = []
    for item in preferences:
        x = [item.id, item.type, item.allergy]
        y += [x]
    preferences_df = pd.DataFrame(y, columns=['id', 'type', 'allergy'])
    for index, row in recommender.iterrows():
        if str(preferences_df.iat[0, 2]) == 'قمح':
            all = ['قمح', 'دقيق', 'طحين', 'خبز']
            for i in all:
                check = " " + i + " "
                if check in (" " + row['Ingredients'] + " "):
                    recipeId = row['recipeId']
                    recommender = recommender.set_index('recipeId')
                    recommender = recommender.drop(index=recipeId)
                    recommender['recipeId'] = recommender.index
                    recommender.index = range(len(recommender))
                    continue

        if str(preferences_df.iat[0, 2]) == 'بيض':
            all = ['بيضتان', 'بيضتين', 'بيضات', 'بيض']
            for i in all:
                check = " " + i + " "
                if check in (" " + row['Ingredients'] + " "):
                    recipeId = row['recipeId']
                    recommender = recommender.set_index('recipeId')
                    recommender = recommender.drop(index=recipeId)
                    recommender['recipeId'] = recommender.index
                    recommender.index = range(len(recommender))
                    continue

        if str(preferences_df.iat[0, 2]) == 'حليب':
            all = ['حليب']
            for i in all:
                check = " " + i + " "
                if check in (" " + row['Ingredients'] + " "):
                    recipeId = row['recipeId']
                    recommender = recommender.set_index('recipeId')
                    recommender = recommender.drop(index=recipeId)
                    recommender['recipeId'] = recommender.index
                    recommender.index = range(len(recommender))
                    continue

    recommender.index = range(len(recommender))
    recipe_recommender = []
    for i in recommender['recipeId']:
        recipe_recommender += (recipes.objects.filter(pk=i))

    return recipe_recommender



def profile(request):
    # This function is based on returning the user's personal information from the Database and displaying it on the HTML page
    if request.user.is_authenticated:
        list =[]
        Ratingrecipe = Rating1.objects.filter(user=request.user.id)
        B= []
        y = []
        for item in Ratingrecipe:
            A = [item.user.id, item.recipe, item.rating ]
            B += [A]
        Ratingrecipe_df= pd.DataFrame(B, columns=['userId', 'recipeId', 'rating'])

        for item in Ratingrecipe_df['recipeId'] :
            recipe = recipes.objects.filter(id=item.id)
            list += recipe
            x = [item.id, item.name, item.Ingredients, item.recipesduration, item.sections, item.description,
                     item.image]
            y += [x]
        recipe_df = pd.DataFrame(y, columns=['recipeId', 'name', 'Ingredients', 'recipesduration', 'sections',
                                             'description', 'image'])
        totalReview = Rating1.objects.filter(user=request.user.id).count()
        return render(request, 'profile.html',
                      {'totalReview': totalReview, 'Ratingrecipe': Ratingrecipe , 'list':list})
    else:
        return HttpResponseRedirect('login')




def recipes_page(request):
    # This function is to display all the recipes stored in the Database on the recipes page
    recipes_info = recipes.objects.all()
    return render(request, 'recipes.html',{'recipes_info':recipes_info})



from django.shortcuts import render

# Create your views here.
